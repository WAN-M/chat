import logging

from typing import Any
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .chat_models import OllamaModel

LOGGER = logging.getLogger(__name__)

# Create your views here.
class ChatView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._model = OllamaModel()

    def post(self, request: Request):
        message = request.data.get('message', None)
        # message = request.query_params.get('message', None)
        if message:
            LOGGER.info(f"Receive Message: {message}")
            try:
                reply = self._model.chat_response(message)
            except Exception as e:
                LOGGER.error(str(e))
                return Response({"error": "exception happened"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            LOGGER.info(f'Reply: {reply}')
            return Response({"reply": reply}, status=status.HTTP_200_OK)
        return Response({"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST)
    
class DebugView(APIView):
    def get(self, request):
        LOGGER.info('Successfully Get Request!')
        return Response(status=status.HTTP_200_OK)
