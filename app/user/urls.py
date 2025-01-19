from django.urls import path
from .views import SignUpAPI, UserListAPI

urlpatterns = [
    path('', UserListAPI.as_view()),
    path('signup', SignUpAPI.as_view()),
]
