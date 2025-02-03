from celery import shared_task
from django.core.cache import cache
from todo.models import Todo

CACHE_WRITE_BACK_KEY = "pending_db_updates"


@shared_task
def flush_cache_to_db():
    """일정 주기마다 캐시 데이터를 DB에 반영 (Write-Back)"""
    pending_updates = cache.get(CACHE_WRITE_BACK_KEY, {})

    if not pending_updates:
        print("No pending updates.")
        return "No updates"

    for todo_id, data in pending_updates.items():
        todo = Todo.objects.get(id=todo_id)

        for key, value in data.items():
            setattr(todo, key, value)
        todo.save()

    cache.delete(CACHE_WRITE_BACK_KEY)

    return f"{len(pending_updates)} tasks updated in DB"
