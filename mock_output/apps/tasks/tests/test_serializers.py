from django.test import TestCase
from apps.users.models import User
from apps.tasks.models import Task
from apps.tasks.serializers import TaskListSerializer


class TaskSerializerTest(TestCase):
    def test_list_serializer_fields(self):
        user = User.objects.create_user(username="u", email="u@example.com", password="p")
        task = Task.objects.create(title="My task", owner=user)
        data = TaskListSerializer(task).data
        self.assertIn("title", data)
        self.assertIn("status", data)
