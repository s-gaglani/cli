from django.test import TestCase
from rest_framework.test import APIClient
from apps.users.models import User
from apps.tasks.models import Task


class TaskViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="u", email="u@example.com", password="p")
        self.client.force_authenticate(user=self.user)
        Task.objects.create(title="Task 1", owner=self.user)

    def test_list_own_tasks(self):
        response = self.client.get("/api/v1/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_task(self):
        payload = {"title": "New task", "priority": "high"}
        response = self.client.post("/api/v1/tasks/", payload)
        self.assertEqual(response.status_code, 201)
