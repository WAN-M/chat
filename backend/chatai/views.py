import logging
import json
from typing import Any
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .chat_models import OllamaModel
from user.models import Message, Session

LOGGER = logging.getLogger(__name__)

# Create your views here.
class ChatView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._model = OllamaModel()

    def _event_stream(self, message):
        finished = False
        # TODO 完善结束逻辑
        for token in self._model.chat_stream(message):
            result_data = {
                'result': {
                    'output': {
                        'content': token
                    },
                    'metadata': {
                        'finishReason': 'stop' if finished else 'continue'
                    }
                }
            }
            
            if token == "结束标志":
                finished = True
                result_data['result']['metadata']['finishReason'] = 'stop'

            # 转为 JSON 字符串并发送给前端
            yield f"data: {json.dumps(result_data)}\n\n"

        # 流结束后确保发送 finishReason 为 'stop'
        if not finished:
            yield f"data: {json.dumps({'result': {'output': {'content': ''}, 'metadata': {'finishReason': 'stop'}}})}\n\n"

    def post(self, request: Request):
        message = request.data.get('message', None)
        session_id = request.data.get('session_id', None)
        if not message or not session_id:
            return Response({"message": "参数错误"}, status=status.HTTP_400_BAD_REQUEST)
        
        LOGGER.info(f"Receive Session {session_id}\nMessage: {message}")
        session = Session.objects.get(id=session_id)
        Message.objects.create(session=session, role='user', content=message)
        return StreamingHttpResponse(self._event_stream(message), content_type='text/event-stream')
    
class DebugView(APIView):
    def get(self, request):
        LOGGER.info('Successfully Get Request!')
        return Response(status=status.HTTP_200_OK)
