import logging
import random
import string
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

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
        
        try:
            user = User.objects.get(email=email, password=password)
        except User.DoesNotExist:
            return Response({'message': '邮箱或密码错误', 'code': 401}, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        token = refresh.access_token
        token.set_exp(lifetime=timedelta(minutes=30))

        response = Response({'token': str(token), 'code': 200}, status=status.HTTP_200_OK)
        response.set_cookie('token', token, httponly=True, expires=timezone.now() + timedelta(minutes=30))
        return response
