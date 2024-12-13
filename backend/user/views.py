import logging
import random
import string

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django_redis import get_redis_connection
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import User

LOGGER = logging.getLogger(__name__)
# 连接 Redis
redis_connection = get_redis_connection("default")

class RegisterView(APIView):
    def post(self, request: Request):
        nickname = request.POST.get('nickname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        verification_code = request.POST.get('verification_code')

        # 从 Redis 获取验证码
        redis_code = redis_connection.get(email)
        if not redis_code:
            return Response({'error': 'Verification code has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        if verification_code != redis_code.decode():
            return Response({'error': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 删除验证码
        redis_connection.delete(email)  

        # 创建用户
        user = User.objects.create(
            nickname=nickname,
            email=email,
            password=make_password(password)
        )
        return Response(status=status.HTTP_200_OK)

class EmailView(APIView):
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
            return Response({'message': 'please enter a valid email'}, status=status.HTTP_400_BAD_REQUEST)

        # 生成并存储验证码
        code = self._generate_verification_code()
        redis_connection.setex(email, 180, code)  # 存储3分钟过期的验证码
        LOGGER.info(f'Generate Code {code} for Email {email}')

        # 发送验证码到用户邮箱
        self._send_verification_email(email, code)
        return Response(status=status.HTTP_200_OK)
