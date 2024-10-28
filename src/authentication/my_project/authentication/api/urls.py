from django.urls import path
from authentication.views import ProtectedView, LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', ProtectedView.as_view(), name='protected'),
]
