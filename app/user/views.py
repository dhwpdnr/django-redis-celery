from django.contrib.auth import get_user_model
from django.core.cache import cache

from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import UserSerializer, UserReadSerializer
from .tasks import send_email_task

User = get_user_model()


class SignUpAPI(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = User.objects.create_user(username=serializer.validated_data["username"],
                                        email=serializer.validated_data["email"],
                                        password=serializer.validated_data["password"])
        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        # 오래걸리는 작업
        subject = "Welcome"
        body = f"Welcome {instance.username}"
        task = send_email_task.delay(subject, body, instance.email)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserListAPI(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserReadSerializer

    def get(self, request):
        cache_key = "user_list_cache"
        cached_users = cache.get(cache_key)

        if cached_users:
            return Response(cached_users, status=status.HTTP_200_OK)

        users = User.objects.all().values("id", "username", "email")
        user_list = list(users)

        cache.set(cache_key, user_list, timeout=300)  # 300초 (5분)

        return Response(user_list, status=status.HTTP_200_OK)
