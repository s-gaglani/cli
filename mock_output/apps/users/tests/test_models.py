from django.test import TestCase
from apps.users.models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="pass")

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(str(self.user), self.user.email)
