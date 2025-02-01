import time
from django.test import TestCase
from django.core.cache import cache
from django.test.utils import CaptureQueriesContext
from django.db import connection
from .models import Task


class TestTask(TestCase):
    def setUp(self):
        cache.clear()
        return super().setUp()

    def test_task_list_caching(self):
        """Task 목록 API 캐싱"""
        Task.objects.create(title="Task 1")
        Task.objects.create(title="Task 2")
        Task.objects.create(title="Task 3")

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get("/api/todo/task")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.json()), 3)
        self.assertEqual(len(queries), 1)

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get("/api/todo/task")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        self.assertEqual(len(queries), 0)

        time.sleep(3)

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get("/api/todo/task")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.json()), 3)
        self.assertEqual(len(queries), 1)

    def test_task_create_rate_limit(self):
        """Task 생성 API 요청 제한"""
        response = self.client.post("/api/todo/task/create", {"title": "Task"})
        self.assertEqual(response.status_code, 201)
        response = self.client.post("/api/todo/task/create", {"title": "Task"})
        self.assertEqual(response.status_code, 429)

        time.sleep(1)

        response = self.client.post("/api/todo/task/create", {"title": "Task"})
        self.assertEqual(response.status_code, 201)

    def test_task_detail_caching(self):
        """Task 상세 정보 API 캐싱"""
        task = Task.objects.create(title="Task 1")

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(f"/api/todo/task/{task.id}")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()["title"], "Task 1")
        self.assertEqual(len(queries), 1)

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(f"/api/todo/task/{task.id}")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()["title"], "Task 1")
        self.assertEqual(len(queries), 0)

    def test_task_update_cache_delete(self):
        """Task 수정 시 캐시 삭제"""
        # Task 생성
        task = Task.objects.create(title="Task 1")

        # Task 상세 정보 조회
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(f"/api/todo/task/{task.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Task 1")
        self.assertEqual(len(queries), 1)

        # Task 상세 정보 조회 (캐시)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(f"/api/todo/task/{task.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Task 1")
        self.assertEqual(len(queries), 0)

        # Task 수정
        payload = {"title": "Task 2"}
        response = self.client.patch(f"/api/todo/task/{task.id}", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        # Task 상세 정보 조회
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(f"/api/todo/task/{task.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Task 2")
        self.assertEqual(len(queries), 1)

    def test_task_delete_cache_delete(self):
        """Task 삭제 시 캐시 삭제"""
        # Task 생성
        task = Task.objects.create(title="Task 1")

        # Task 상세 정보 조회
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(f"/api/todo/task/{task.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Task 1")
        self.assertEqual(len(queries), 1)

        # Task 상세 정보 조회 (캐시)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(f"/api/todo/task/{task.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Task 1")
        self.assertEqual(len(queries), 0)

        # Task 삭제
        response = self.client.delete(f"/api/todo/task/{task.id}")
        self.assertEqual(response.status_code, 204)

        # 캐시 확인
        self.assertIsNone(cache.get(f"task:{task.id}"))
