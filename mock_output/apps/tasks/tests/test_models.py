from django.test import TestCase
from apps.users.models import User
from apps.tasks.models import Task


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", email="u@example.com", password="p")
        self.task = Task.objects.create(title="Write tests", owner=self.user)

    def test_task_creation(self):
        self.assertEqual(self.task.title, "Write tests")
        self.assertEqual(self.task.status, Task.Status.TODO)
        self.assertEqual(str(self.task), "Write tests")
