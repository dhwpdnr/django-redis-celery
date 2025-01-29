import random
from celery import shared_task
from django.core.cache import cache
from .models import Task
from .serializers import TaskSerializer


@shared_task
def warm_cache_task():
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)

    cache_key = "tasks_list"
    cache.set(cache_key, serializer.data, timeout=3600)  # Cache for 1 hour
    print(f"Cache warmed for key: {cache_key}")


@shared_task
def warm_cache_task_detail():
    tasks = Task.objects.all()
    for task in tasks:
        jitter = random.randint(0, 300)  # 최대 5분 랜덤 지연
        cache_key = f"task_detail:{task.id}"
        serializer = TaskSerializer(task)
        cache.set(cache_key, serializer.data, timeout=3600 + jitter)
