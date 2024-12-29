import logging
import json
from typing import Any
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .chat_models import OllamaModel, ElasticSearchRAG, RAG, VectoreDatabase

from user.models import Message, Session

LOGGER = logging.getLogger(__name__)

# Create your views here.
class ChatView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._model = OllamaModel()
        self._use_rag = True

    def _event_stream(self, message):
        finished = False
        for token in self._model.chat_stream(message):
            result_data = {
                'result': {
                    'output': {
                        'content': token
                    },
                    'metadata': {
                        'finishReason': 'continue'
                    }
                }
            }
            yield f"data: {json.dumps(result_data)}\n\n" # SSE需要\n\n

        if not finished:
            yield f"data: {json.dumps({'result': {'output': {'content': ''}, 'metadata': {'finishReason': 'stop'}}})}\n\n"

    def _event_stream_rag(self, message, user):
        releated_docs = ElasticSearchRAG.search_documents(message, str(VectoreDatabase.get_db_dir(user) / 'vector'))
        LOGGER.info(f'Find {len(releated_docs)} file blocks')
        for doc in releated_docs:
            LOGGER.info(doc)

        finished = False
        for token in self._model.chat_stream_rag(message, releated_docs):
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
            yield f"data: {json.dumps(result_data)}\n\n"

        if not finished:
            yield f"data: {json.dumps({'result': {'output': {'content': ''}, 'metadata': {'finishReason': 'stop'}}})}\n\n"

    def post(self, request: Request):
        message = request.data.get('message', None)
        session_id = request.data.get('session_id', None)
        if not message or not session_id:
            return Response({"message": "参数错误"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        LOGGER.info(f"{user.nickname} Sent Message: {message}")
        session = Session.objects.get(id=session_id)
        Message.objects.create(session=session, role='user', content=message)

        return StreamingHttpResponse(self._event_stream_rag(message, user) if self._use_rag else self._event_stream(message), 
                                     content_type='text/event-stream')
    
class DebugView(APIView):
    def get(self, request):
        LOGGER.info('Successfully Get Request!')
        return Response(status=status.HTTP_200_OK)
