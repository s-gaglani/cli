"""
Tests for evaluation app serializers.
"""
import uuid
from django.test import TestCase
from apps.evaluation.serializers import (
    EvaluateRequestSerializer,
    EvaluateBulkRequestSerializer,
    EvaluationLogSerializer,
)
from apps.evaluation.models import EvaluationLog


class EvaluateRequestSerializerTest(TestCase):
    """Tests for EvaluateRequestSerializer."""

    def _valid_data(self, **overrides):
        data = {
            "project_id": str(uuid.uuid4()),
            "environment_key": "production",
            "flag_key": "my-flag",
            "user_key": "user-123",
            "attributes": {"plan": "premium"},
        }
        data.update(overrides)
        return data

    def test_valid_data_passes(self):
        """Serializer is valid when all required fields are provided."""
        s = EvaluateRequestSerializer(data=self._valid_data())
        self.assertTrue(s.is_valid(), s.errors)

    def test_attributes_defaults_to_empty_dict(self):
        """attributes defaults to {} when not provided."""
        data = self._valid_data()
        del data["attributes"]
        s = EvaluateRequestSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["attributes"], {})

    def test_missing_project_id_fails(self):
        data = self._valid_data()
        del data["project_id"]
        s = EvaluateRequestSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("project_id", s.errors)

    def test_invalid_uuid_project_id_fails(self):
        s = EvaluateRequestSerializer(data=self._valid_data(project_id="not-a-uuid"))
        self.assertFalse(s.is_valid())
        self.assertIn("project_id", s.errors)

    def test_missing_environment_key_fails(self):
        data = self._valid_data()
        del data["environment_key"]
        s = EvaluateRequestSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("environment_key", s.errors)

    def test_blank_environment_key_fails(self):
        s = EvaluateRequestSerializer(data=self._valid_data(environment_key="   "))
        self.assertFalse(s.is_valid())
        self.assertIn("environment_key", s.errors)

    def test_missing_flag_key_fails(self):
        data = self._valid_data()
        del data["flag_key"]
        s = EvaluateRequestSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("flag_key", s.errors)

    def test_blank_flag_key_fails(self):
        s = EvaluateRequestSerializer(data=self._valid_data(flag_key=""))
        self.assertFalse(s.is_valid())
        self.assertIn("flag_key", s.errors)

    def test_missing_user_key_fails(self):
        data = self._valid_data()
        del data["user_key"]
        s = EvaluateRequestSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("user_key", s.errors)

    def test_blank_user_key_fails(self):
        s = EvaluateRequestSerializer(data=self._valid_data(user_key=""))
        self.assertFalse(s.is_valid())
        self.assertIn("user_key", s.errors)

    def test_whitespace_stripped_from_keys(self):
        """Whitespace is stripped from environment_key, flag_key, user_key."""
        s = EvaluateRequestSerializer(data=self._valid_data(
            environment_key="  production  ",
            flag_key="  my-flag  ",
            user_key="  user-123  ",
        ))
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["environment_key"], "production")
        self.assertEqual(s.validated_data["flag_key"], "my-flag")
        self.assertEqual(s.validated_data["user_key"], "user-123")

    def test_attributes_can_be_nested(self):
        """attributes accepts nested JSON."""
        s = EvaluateRequestSerializer(data=self._valid_data(
            attributes={"plan": "pro", "tags": ["a", "b"], "meta": {"x": 1}}
        ))
        self.assertTrue(s.is_valid(), s.errors)


class EvaluateBulkRequestSerializerTest(TestCase):
    """Tests for EvaluateBulkRequestSerializer."""

    def _valid_data(self, **overrides):
        data = {
            "project_id": str(uuid.uuid4()),
            "environment_key": "staging",
            "flag_keys": ["flag-a", "flag-b"],
            "user_key": "user-456",
            "attributes": {},
        }
        data.update(overrides)
        return data

    def test_valid_data_passes(self):
        s = EvaluateBulkRequestSerializer(data=self._valid_data())
        self.assertTrue(s.is_valid(), s.errors)

    def test_empty_flag_keys_fails(self):
        s = EvaluateBulkRequestSerializer(data=self._valid_data(flag_keys=[]))
        self.assertFalse(s.is_valid())
        self.assertIn("flag_keys", s.errors)

    def test_whitespace_only_flag_keys_fails(self):
        s = EvaluateBulkRequestSerializer(data=self._valid_data(flag_keys=["  ", ""]))
        self.assertFalse(s.is_valid())
        self.assertIn("flag_keys", s.errors)

    def test_flag_keys_stripped(self):
        s = EvaluateBulkRequestSerializer(data=self._valid_data(
            flag_keys=["  flag-a  ", "flag-b"]
        ))
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["flag_keys"], ["flag-a", "flag-b"])

    def test_missing_user_key_fails(self):
        data = self._valid_data()
        del data["user_key"]
        s = EvaluateBulkRequestSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("user_key", s.errors)


class EvaluationLogSerializerTest(TestCase):
    """Tests for EvaluationLogSerializer."""

    def test_serializes_log(self):
        """Serializer correctly represents an EvaluationLog."""
        log = EvaluationLog.objects.create(
            project_id=uuid.uuid4(),
            environment_key="production",
            flag_key="feature-x",
            user_key="user-789",
            result_value=True,
            reason="DEFAULT",
        )
        s = EvaluationLogSerializer(log)
        data = s.data
        self.assertEqual(data["flag_key"], "feature-x")
        self.assertEqual(data["user_key"], "user-789")
        self.assertEqual(data["reason"], "DEFAULT")
        self.assertEqual(data["result_value"], True)
        self.assertIn("id", data)
        self.assertIn("evaluated_at", data)
