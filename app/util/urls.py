from django.urls import path
from .views import APICountView

urlpatterns = [
    path('api-count', APICountView.as_view()),
]
