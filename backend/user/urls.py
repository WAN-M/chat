from django.urls import path
from .views import EmailView, RegisterView, LoginView, SessionView, MessageView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('send_code/', EmailView.as_view(), name='send_code'),
    path('login/', LoginView.as_view(), name='login'),
    path('session/', SessionView.as_view({'get': 'list', 'post': 'create'}), name='all-session'),
    path('session/<int:session_id>/', SessionView.as_view({'delete': 'destroy'}), name='delete-session'),
    path('message/<int:session_id>/', MessageView.as_view({'get': 'list'}, name='all-message')),
    path('message/', MessageView.as_view({'post': 'create'}), name='new-message'),
]
