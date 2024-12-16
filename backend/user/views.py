import logging
import random
import string
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework.mixins import ListModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Session, Message
from .serializers import MessageSerializer

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
        user = User.objects.create(
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
        token.set_exp(lifetime=timedelta(minutes=30))

        response = Response({'token': str(token), 'code': 200}, status=status.HTTP_200_OK)
        response.set_cookie('token', token, httponly=True, expires=timezone.now() + timedelta(minutes=30))
        return response

class SessionView(DestroyModelMixin, ListModelMixin):
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
        session_id = request.data.get('session_id')
        user = request.user

        try:
            session = Session.objects.get(id=session_id, user=user)
            session.is_visible = False
            session.save()
            return Response({"message": "删除成功"}, status=status.HTTP_200_OK)
        except Session.DoesNotExist:
            return Response({"message": "会话不存在"}, status=status.HTTP_404_NOT_FOUND)

class MessageView(CreateModelMixin, ListModelMixin):
    """
    API to create a new message in a specific session.
    """
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        session_id = request.data.get('session_id')

        try:
            session = Session.objects.get(id=session_id, user=user)
        except Session.DoesNotExist:
            return Response({"message": "会话不存在"}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'session': session.id,
            'role': request.data.get('role', 'Model'),
            'content': request.data.get('content', '')
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({'message': '创建成功'}, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        user = request.user
        session_id = request.query_params.get('session_id', None)

        if not session_id:
            return Response({'message': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)

        messages = Message.objects.filter(session_id=session_id, session__user=user)
        messages = messages.order_by('created_at')  # 升序排序，最早的消息排前面

        serializer = self.get_serializer(messages, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
