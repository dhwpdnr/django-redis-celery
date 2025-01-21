from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer


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

#
#   rate_limit_key = f"rate_limit:{client_ip}"  # Redis에 저장할 키 생성
#
#     # Redis에서 키 확인
#     if redis_client.exists(rate_limit_key):
#         # 키가 존재하면 요청 제한
#         ttl = redis_client.ttl(rate_limit_key)
#         return JsonResponse(
#             {"error": f"Too many requests. Try again in {ttl} seconds."},
#             status=429
#         )
#
#     # 키가 없으면 요청 허용 및 TTL 설정 (1초 동안 유효)
#     redis_client.set(rate_limit_key, 1, ex=1)


# def rate_limited_view(request):
#     client_ip = request.META['REMOTE_ADDR']
#     key = f"rate_limit:{client_ip}"
#
#     # 현재 요청 수 가져오기
#     current_count = redis_client.get(key)
#     if current_count and int(current_count) >= 5:  # 5초에 5회 요청 제한
#         return JsonResponse({"error": "Too many requests. Please try again later."}, status=429)
#
#     # 요청 수 증가 및 만료 시간 설정 (5초 TTL)
#     redis_client.incr(key)
#     redis_client.expire(key, 5)
#
#     return JsonResponse({"message": "Request successful"})
