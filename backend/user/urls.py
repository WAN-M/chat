from django.urls import path
from .views import EmailView, RegisterView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('send_code/', EmailView.as_view(), name='send_code'),
    path('login/', LoginView.as_view(), name='login'),
]
