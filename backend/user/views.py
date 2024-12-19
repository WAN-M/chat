import logging
import os
import random
import shutil
import string
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework.mixins import ListModelMixin, DestroyModelMixin, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Session, Message
from .serializers import MessageSerializer, UserSerializer
from chatai.file_parser.parser_factory import ParserFactory
from chatai.chat_models.vector_db import VectoreDatabase

LOGGER = logging.getLogger(__name__)
# 连接 Redis
redis_connection = get_redis_connection("default")

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request):
        nickname = request.data.get('nickname')
        email = request.data.get('email')
        password = request.data.get('password')
        verifyCode = request.data.get('verifyCode')

        LOGGER.info(f'Register Request From {email}, VerifyCode is {verifyCode}')

        # 从 Redis 获取验证码
        redis_code = redis_connection.get(email)
        if not redis_code:
            return Response({'message': '验证码过期，请重新发送', 'code': '400'}, status=status.HTTP_400_BAD_REQUEST)

        if verifyCode != redis_code.decode():
            return Response({'message': '验证码错误', 'code': 400}, status=status.HTTP_400_BAD_REQUEST)
        
        # 删除验证码
        redis_connection.delete(email)  

        # 创建用户
        User.objects.create_user(
            nickname=nickname,
            email=email,
            password=password
        )
        return Response(status=status.HTTP_200_OK)

class EmailView(APIView):
    permission_classes = [AllowAny]

    def _generate_verification_code(self, length=6):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))
    
    def _send_verification_email(self, email, code):
        subject = 'Your Verification Code'
        message = f'Your verification code is {code}.'
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [email])

    def post(self, request: Request):
        email = request.data.get('email', None)

        if not email:
            return Response({'message': '请输入有效邮箱', 'code': 400}, status=status.HTTP_400_BAD_REQUEST)

        # 生成并存储验证码
        code = self._generate_verification_code()
        redis_connection.setex(email, 180, code)  # 存储3分钟过期的验证码
        LOGGER.info(f'Generate Code {code} for Email {email}')

        # 发送验证码到用户邮箱
        self._send_verification_email(email, code)
        return Response({'code': 200}, status=status.HTTP_200_OK)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        if not email or not password:
            return Response({'message': '未提供完整信息', 'code': 400}, status=status.HTTP_400_BAD_REQUEST)
        
        LOGGER.info(f'{email} Login')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': '邮箱未注册', 'code': 401}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({'message': '邮箱或密码错误', 'code': 401}, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        token = refresh.access_token
        token.set_exp(lifetime=timedelta(minutes=settings.TOKEN_EXPIRATION))

        response = Response({'token': str(token), 'code': 200}, status=status.HTTP_200_OK)
        response.set_cookie('token', token, httponly=True, expires=timezone.now() + timedelta(minutes=settings.TOKEN_EXPIRATION))
        return response

class SessionView(CreateModelMixin, 
                  DestroyModelMixin, 
                  ListModelMixin, 
                  UpdateModelMixin,
                  GenericViewSet):
    def create(self, request, *args, **kwargs):
        """
        Create a new session for user
        """
        user = request.user
        Session.objects.create(user=user, session_name='新对话')
        return Response(status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """
        Update session name
        """
        user = request.user
        session_id = kwargs.get('session_id')
        session_name = request.data.get('session_name', None)

        if not session_name:
            return Response({"message": "参数错误"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = Session.objects.get(id=session_id, user=user)
        except Session.DoesNotExist:
            return Response({"message": "会话不存在"}, status=status.HTTP_404_NOT_FOUND)

        session.session_name = session_name
        session.save()

        return Response({"message": "会话更新成功"}, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        """
        List all visible sessions for user.
        """
        user = request.user
        sessions = Session.objects.filter(user=user, is_visible=True).order_by('-created_at')

        session_data = [
            {
                'id': session.id,
                'session_name': session.session_name,
                'created_at': session.created_at,
                'updated_at': session.updated_at,
            }
            for session in sessions
        ]

        return Response(session_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Instead of deleting the session, mark it as not visible.
        """
        session_id = kwargs.get('session_id')
        user = request.user

        try:
            session = Session.objects.get(id=session_id, user=user)
            session.is_visible = False
            session.save()
            return Response({"message": "删除成功"}, status=status.HTTP_200_OK)
        except Session.DoesNotExist:
            return Response({"message": "会话不存在"}, status=status.HTTP_404_NOT_FOUND)

class MessageView(CreateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = MessageSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new message in a specific session.
        """
        user = request.user
        session_id = request.data.get('session_id')
        LOGGER.info(request.data)
        try:
            session = Session.objects.get(id=session_id, user=user)
        except Session.DoesNotExist:
            return Response({"message": "会话不存在"}, status=status.HTTP_404_NOT_FOUND)

        Message.objects.create(
            session=session, 
            role=request.data.get('role', 'model'), 
            content=request.data.get('content', ''))

        return Response({'message': '创建成功'}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """
        Show all messages in a session asc by create_time
        """
        user = request.user
        session_id = kwargs.get('session_id', None)

        if not session_id:
            return Response({'message': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)

        messages = Message.objects.filter(session_id=session_id, session__user=user)
        messages = messages.order_by('created_at')

        serializer = self.get_serializer(messages, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserView(RetrieveModelMixin, GenericViewSet):
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class KnowledgeView(CreateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    parser_classes = (MultiPartParser, FormParser)  # 允许解析multipart/form-data

    def _vectorize_doc(self, file_path, vector_path):
        parser = ParserFactory.get_parser(file_path)()
        docs = parser.parse(file_path)
        VectoreDatabase.store(docs, str(vector_path))

    def create(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'message': '未收到文件'}, status=400)

        # store file to /xxx/email/xxx path
        dir = VectoreDatabase.get_db_dir(request.user)
        if not os.path.exists(dir):
            os.makedirs(dir)
            os.makedirs(dir / 'file')
            os.makedirs(dir / 'vector')
        file_path = dir / 'file' / file.name
        vector_path = dir / 'vector' / file.name.split('.')[0]
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(vector_path):
            shutil.rmtree(vector_path)
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        self._vectorize_doc(file_path, vector_path)

        return Response({'message': '文件上传成功'}, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        knowledge_name = kwargs.get('knowledge_name')
        dir = VectoreDatabase.get_db_dir(request.user)
        file_dir = dir / 'file'
        vector_dir = dir / 'vector'
        rm_dir = file_dir / 'remove'
        if not os.path.exists(rm_dir):
            os.makedirs(rm_dir)
        shutil.move(file_dir / knowledge_name, rm_dir / knowledge_name)
        shutil.rmtree(vector_dir / knowledge_name.split('.')[0])
        return Response({'message': '知识库删除成功'}, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        dir = VectoreDatabase.get_db_dir(request.user) / 'file'
        if os.path.exists(dir):
            file_names = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
        else:
            file_names = []
        return Response(file_names, status=status.HTTP_200_OK)
