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
        response = self.client.post("/api/todo/task/create", {"title": "Task"})
        self.assertEqual(response.status_code, 201)
        response = self.client.post("/api/todo/task/create", {"title": "Task"})
        self.assertEqual(response.status_code, 429)

        time.sleep(1)

        response = self.client.post("/api/todo/task/create", {"title": "Task"})
        self.assertEqual(response.status_code, 201)

    def test_task_detail_caching(self):
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
        #
        # time.sleep(3)
        #
        # with CaptureQueriesContext(connection) as queries:
        #     response = self.client.get(f"/api/todo/task/{task.id}")
        # self.assertEqual(response.status_code, 200)
        #
        # self.assertEqual(response.json()["title"], "Task 1")
        # self.assertEqual(len(queries), 1)
