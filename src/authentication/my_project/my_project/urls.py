from django.urls import path
from src.authentication.my_project.authentication.views import (
    LoginView, ProtectedView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', ProtectedView.as_view(), name='protected'),
]
