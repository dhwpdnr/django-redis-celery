from django.urls import path, include
from .views import SignUpAPI

urlpatterns = [
    path('signup', SignUpAPI.as_view()),
]
