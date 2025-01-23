from django.core.cache import cache


class APICountMiddleware:
    """API 요청 수를 카운트하는 미들웨어"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        api_path = request.path
        redis_key = f"api_count:{api_path}"

        if cache.get(redis_key) is None:
            cache.set(redis_key, 0)

        cache.incr(redis_key)

        response = self.get_response(request)
        return response
