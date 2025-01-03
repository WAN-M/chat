from django.urls import path
from .views import EmailView, RegisterView, LoginView, SessionView, MessageView, UserView, KnowledgeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('send_code/', EmailView.as_view(), name='send_code'),
    path('login/', LoginView.as_view(), name='login'),
    path('session/', SessionView.as_view({'get': 'list', 'post': 'create'}), name='all-session'),
    path('session/<int:session_id>/', SessionView.as_view({'delete': 'destroy', 'put': 'update'}), name='delete-session'),
    path('message/<int:session_id>/', MessageView.as_view({'get': 'list'}, name='all-message')),
    path('message/', MessageView.as_view({'post': 'create'}), name='new-message'),
    path('info/', UserView.as_view({'get': 'retrieve'}), name='user-info'),
    path('knowledge/', KnowledgeView.as_view({'get': 'list', 'post': 'create'}), name='upload-knowledge'),
    path('knowledge/<str:knowledge_name>/', KnowledgeView.as_view({'delete': 'destroy'}), name='delete-knowledge'),
]
