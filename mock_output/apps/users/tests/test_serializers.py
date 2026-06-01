from django.test import TestCase
from apps.users.models import User
from apps.users.serializers import UserDetailSerializer


class UserSerializerTest(TestCase):
    def test_serializer_fields(self):
        user = User.objects.create_user(username="u", email="u@example.com", password="p")
        data = UserDetailSerializer(user).data
        self.assertIn("email", data)
        self.assertIn("username", data)
