import os
import datetime
from celery import shared_task
import redis


@shared_task
def backup_redis_rdb():
    backup_dir = "/var/lib/redis/backups"
    rdb_path = "/var/lib/redis/dump.rdb"

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{backup_dir}/dump_{timestamp}.rdb"

    if os.path.exists(rdb_path):
        os.rename(rdb_path, backup_path)

    # 새로운 RDB 저장
    redis_client = redis.Redis(host='localhost', port=6379)
    redis_client.bgsave()

    # 최대 5개까지만 유지 → 오래된 백업 삭제
    backups = sorted(os.listdir(backup_dir))
    if len(backups) > 5:
        os.remove(os.path.join(backup_dir, backups[0]))

    return f"Redis RDB 스냅샷 저장 완료: {backup_path}, 현재 저장 개수: {len(backups)}"
