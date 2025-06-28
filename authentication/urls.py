from django.urls import path
from authentication.views import (
    UserRegisterView,
    UserLoginView,
    UserRecoveryView,
    OtpVerifyView,
    ResetPasswordView
)

app_name = 'authentication'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('recovery/', UserRecoveryView.as_view(), name='recovery'),
    path('otp-verify/', OtpVerifyView.as_view(), name='otp_verify'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]