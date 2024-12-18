from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from user.models import User

import logging
LOGGER = logging.getLogger(__name__)

# 从请求的 Cookie 中提取 Token
class CookieJWTAuthentication(JWTAuthentication):
    def get_user(self, validate_token):
        try:
            user_id = validate_token['user_id']
        except KeyError:
            raise AuthenticationFailed('Token is invalid or expired')
        try:
            user = User.objects.get(**{'id': user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed('Token is invalid or expired')
        return user

    def authenticate(self, request):
        token = request.COOKIES.get('token')
        if not token:
            return None

        try:
            validated_token = self.get_validated_token(token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except Exception as e:
            LOGGER.error(str(e))
            raise AuthenticationFailed('Token is invalid or expired')
