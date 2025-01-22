from django.urls import path
from .views import SignUpAPI, UserListAPI, GenerateOTPAPI, VerifyOTPAPI

urlpatterns = [
    path('', UserListAPI.as_view()),
    path('signup', SignUpAPI.as_view()),
    path('generate-otp', GenerateOTPAPI.as_view()),
    path('verify-otp', VerifyOTPAPI.as_view()),
]
