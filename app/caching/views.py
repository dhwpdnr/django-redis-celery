from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response
from todo.models import Todo
from todo.serializers import TodoSerializer
import json

CACHE_WRITE_BACK_KEY = "pending_db_updates"


def write_to_cache(task_id, data):
    """
    데이터를 캐시에 저장 (DB에는 즉시 반영하지 않음)
    """
    cache_key = f"task:{task_id}"
    cache.set(cache_key, data, timeout=3600)  # 1시간 유지

    pending_updates = cache.get(CACHE_WRITE_BACK_KEY, {})
    pending_updates[task_id] = data
    cache.set(CACHE_WRITE_BACK_KEY, pending_updates, timeout=3600)  # 1시간 유지


class TodoDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

    def get(self, request, *args, **kwargs):
        todo_id = kwargs['pk']
        cache_key = f"todo:{todo_id}"
        cached_todo = cache.get(cache_key)

        if cached_todo:
            print("Cache Hit!")
            return Response(cached_todo)

        print("Cache Miss! Fetching from database...")
        try:
            todo = Todo.objects.get(id=todo_id)
            serializer = self.get_serializer(todo)

            # DB 데이터를 캐시에 저장
            cache.set(cache_key, serializer.data, timeout=3600)

            return Response(serializer.data)
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=404)

    def update(self, request, *args, **kwargs):
        todo_id = kwargs['pk']
        try:
            todo = Todo.objects.get(id=todo_id)
            serializer = self.get_serializer(todo, data=request.data, partial=True)

            if serializer.is_valid():
                updated_data = serializer.validated_data
                updated_data["id"] = todo.id  # Task ID 추가

                # ✅ 변경된 데이터를 캐시에 저장 (즉시 DB 반영 X)
                write_to_cache(todo_id, updated_data)

                return Response(updated_data, status=200)
            return Response(serializer.errors, status=400)

        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=404)
