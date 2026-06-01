from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User


class UserViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username="admin", email="a@example.com", password="pass")
        self.client.force_authenticate(user=self.admin)

    def test_list_users(self):
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, 200)
