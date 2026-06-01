"""
Tests for EvaluationLog model.
"""
import uuid
from django.test import TestCase
from apps.evaluation.models import EvaluationLog


class EvaluationLogModelTest(TestCase):
    """Tests for the EvaluationLog model."""

    def _make_log(self, **kwargs):
        defaults = {
            "project_id": uuid.uuid4(),
            "environment_key": "production",
            "flag_key": "test-flag",
            "user_key": "user-001",
            "result_value": True,
            "reason": "DEFAULT",
        }
        defaults.update(kwargs)
        return EvaluationLog.objects.create(**defaults)

    def test_create_basic_log(self):
        """EvaluationLog can be created with required fields."""
        log = self._make_log()
        self.assertIsNotNone(log.id)
        self.assertIsNotNone(log.evaluated_at)

    def test_uuid_primary_key(self):
        """Primary key is a valid UUID."""
        log = self._make_log()
        self.assertIsInstance(log.id, uuid.UUID)

    def test_auto_now_add_evaluated_at(self):
        """evaluated_at is set automatically on creation."""
        log = self._make_log()
        self.assertIsNotNone(log.evaluated_at)

    def test_str_representation(self):
        """__str__ returns a human-readable string."""
        log = self._make_log(flag_key="my-feature", user_key="bob", reason="DISABLED")
        text = str(log)
        self.assertIn("my-feature", text)
        self.assertIn("bob", text)
        self.assertIn("DISABLED", text)

    def test_default_reason(self):
        """reason defaults to DEFAULT."""
        log = EvaluationLog.objects.create(
            project_id=uuid.uuid4(),
            environment_key="staging",
            flag_key="flag-x",
            user_key="user-xyz",
            result_value=False,
        )
        self.assertEqual(log.reason, "DEFAULT")

    def test_json_result_value_stores_none(self):
        """result_value can store null (None)."""
        log = self._make_log(result_value=None)
        log.refresh_from_db()
        self.assertIsNone(log.result_value)

    def test_json_result_value_stores_dict(self):
        """result_value can store complex JSON."""
        payload = {"variant": "A", "color": "blue"}
        log = self._make_log(result_value=payload)
        log.refresh_from_db()
        self.assertEqual(log.result_value, payload)

    def test_ordering_newest_first(self):
        """Logs are ordered by evaluated_at descending."""
        project = uuid.uuid4()
        log1 = self._make_log(project_id=project, flag_key="flag-a")
        log2 = self._make_log(project_id=project, flag_key="flag-b")
        logs = list(EvaluationLog.objects.filter(project_id=project))
        # Most recent first
        self.assertEqual(logs[0].id, log2.id)
        self.assertEqual(logs[1].id, log1.id)

    def test_all_reason_choices_valid(self):
        """All REASON_CHOICES values can be saved."""
        valid_reasons = [r[0] for r in EvaluationLog.REASON_CHOICES]
        for reason in valid_reasons:
            log = self._make_log(reason=reason)
            log.refresh_from_db()
            self.assertEqual(log.reason, reason)
