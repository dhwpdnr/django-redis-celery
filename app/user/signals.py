from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.core.cache import cache
from django.dispatch import receiver


# 사용자 추가 또는 수정 시 캐시 무효화
@receiver(post_save, sender=User)
def clear_user_cache_on_save(sender, instance, **kwargs):
    cache_key = "user_list_cache"
    cache.delete(cache_key)  # Redis 캐시 삭제


# 사용자 삭제 시 캐시 무효화
@receiver(post_delete, sender=User)
def clear_user_cache_on_delete(sender, instance, **kwargs):
    cache_key = "user_list_cache"
    cache.delete(cache_key)  # Redis 캐시 삭제
