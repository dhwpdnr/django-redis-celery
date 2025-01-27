from django.views.decorators.cache import cache_page
from django.urls import path
from .views import TaskList, CreateTask, TaskDetailAPI

urlpatterns = [
    path("task", cache_page(3)(TaskList.as_view())),
    path("task/<int:pk>", TaskDetailAPI.as_view()),
    path("task/create", CreateTask.as_view()),
]
