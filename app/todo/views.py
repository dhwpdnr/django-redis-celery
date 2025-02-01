from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Task, Todo
from .serializers import TaskSerializer, TodoSerializer


class TaskList(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class CreateTask(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        # 요청 수 증가 및 만료 시간 설정 (5초 TTL)
        client_ip = request.META['REMOTE_ADDR']
        key = f"rate_limit:{client_ip}"

        if cache.get(key):
            ttl = cache.ttl(key)
            return Response({"error": f"Too many requests. Try again in {ttl} seconds."}, status=429)
        cache.set(key, 1, timeout=1)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TaskUpdateDeleteDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get(self, request, *args, **kwargs):
        # 요청 수 증가 및 만료 시간 설정 (5초 TTL)
        task_id = kwargs['pk']
        cache_key = f"task:{task_id}"
        cached_task = cache.get(cache_key)
        if cached_task:
            print("Cache Hit!")
            return Response(cached_task, status=status.HTTP_200_OK)

        print("Cache Miss! Fetching from database...")
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task)

        cache.set(cache_key, serializer.data, timeout=5)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if cache.get(f"task:{instance.id}"):
            cache.delete(f"task:{instance.id}")

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if cache.get(f"task:{instance.id}"):
            cache.delete(f"task:{instance.id}")

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
