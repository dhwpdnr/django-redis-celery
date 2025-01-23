from django.core.cache import cache
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status


class APICountView(generics.GenericAPIView):
    def get(self, request):
        # 쿼리 파라미터에서 api path를 가져옴
        api_path = request.query_params.get("api_path", "")

        redis_key = f"api_count:/{api_path}"
        count = cache.get(redis_key, 0)

        return Response({
            "api_path": f"/{api_path}",
            "request_count": int(count)
        }, status=status.HTTP_200_OK)
