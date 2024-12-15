from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def auth_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            response.data = {
                'code': 'token_not_valid',
                'message': 'Token is invalid or expired. Please log in again.',
                'detail': response.data.get('detail', '')
            }

    return response
