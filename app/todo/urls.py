from django.views.decorators.cache import cache_page
from django.urls import path
from .views import TaskList

urlpatterns = [
    path("task", cache_page(3)(TaskList.as_view())),
]
