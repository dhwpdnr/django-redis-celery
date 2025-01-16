from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django의 기본 settings 모듈을 Celery가 사용하도록 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Django settings에서 Celery 관련 설정을 가져옵니다.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Django 앱에서 task 모듈을 자동으로 탐지합니다.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
