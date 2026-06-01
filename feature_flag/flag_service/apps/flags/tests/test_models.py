"""
Model-level tests for apps.flags.
"""
import uuid

from django.db import IntegrityError
from django.test import TestCase

from apps.flags.models import Flag, TargetingRule, Variation


class FlagModelTest(TestCase):
    def _make_flag(self, **kwargs) -> Flag:
        defaults = {
            "project_id": uuid.uuid4(),
            "environment_key": "production",
            "name": "My Test Flag",
            "key": "my-test-flag",
            "flag_type": "boolean",
            "is_enabled": False,
            "rollout_percentage": 0,
        }
        defaults.update(kwargs)
        return Flag.objects.create(**defaults)

    def test_create_flag_defaults(self):
        flag = self._make_flag()
        self.assertIsNotNone(flag.id)
        self.assertFalse(flag.is_enabled)
        self.assertEqual(flag.rollout_percentage, 0)
        self.assertEqual(flag.flag_type, "boolean")
        self.assertEqual(flag.tags, [])

    def test_flag_str(self):
        flag = self._make_flag()
        self.assertIn("my-test-flag", str(flag))
        self.assertIn("production", str(flag))

    def test_flag_unique_together(self):
        project = uuid.uuid4()
        self._make_flag(project_id=project, environment_key="staging", key="flag-1")
        with self.assertRaises(IntegrityError):
            self._make_flag(project_id=project, environment_key="staging", key="flag-1")

    def test_flag_same_key_different_env(self):
        project = uuid.uuid4()
        f1 = self._make_flag(project_id=project, environment_key="staging", key="flag-x")
        f2 = self._make_flag(project_id=project, environment_key="production", key="flag-x")
        self.assertNotEqual(f1.id, f2.id)

    def test_flag_tags_default_list(self):
        flag = self._make_flag()
        self.assertIsInstance(flag.tags, list)

    def test_flag_ordering(self):
        project = uuid.uuid4()
        f1 = self._make_flag(project_id=project, key="flag-a")
        f2 = self._make_flag(project_id=project, key="flag-b")
        flags = list(Flag.objects.filter(project_id=project))
        # newest first
        self.assertEqual(flags[0].id, f2.id)
        self.assertEqual(flags[1].id, f1.id)


class VariationModelTest(TestCase):
    def setUp(self):
        self.flag = Flag.objects.create(
            project_id=uuid.uuid4(),
            environment_key="production",
            name="Variation Flag",
            key="variation-flag",
        )

    def test_create_variation(self):
        variation = Variation.objects.create(
            flag=self.flag,
            name="Control",
            value={"enabled": False},
            is_control=True,
        )
        self.assertIsNotNone(variation.id)
        self.assertTrue(variation.is_control)
        self.assertEqual(variation.flag, self.flag)

    def test_variation_str(self):
        variation = Variation.objects.create(
            flag=self.flag, name="Treatment", value=True
        )
        self.assertIn("variation-flag", str(variation))
        self.assertIn("Treatment", str(variation))

    def test_variation_cascade_delete(self):
        Variation.objects.create(flag=self.flag, name="V1", value=1)
        self.flag.delete()
        self.assertEqual(Variation.objects.count(), 0)


class TargetingRuleModelTest(TestCase):
    def setUp(self):
        self.flag = Flag.objects.create(
            project_id=uuid.uuid4(),
            environment_key="production",
            name="TR Flag",
            key="tr-flag",
        )
        self.variation = Variation.objects.create(
            flag=self.flag, name="Treatment", value="on"
        )

    def test_create_targeting_rule(self):
        rule = TargetingRule.objects.create(
            flag=self.flag,
            segment_id=uuid.uuid4(),
            variation=self.variation,
            priority=1,
            is_active=True,
        )
        self.assertIsNotNone(rule.id)
        self.assertTrue(rule.is_active)

    def test_targeting_rule_str(self):
        rule = TargetingRule.objects.create(
            flag=self.flag,
            segment_id=uuid.uuid4(),
            variation=self.variation,
            priority=0,
        )
        self.assertIn("tr-flag", str(rule))

    def test_targeting_rule_cascade_delete(self):
        TargetingRule.objects.create(
            flag=self.flag,
            segment_id=uuid.uuid4(),
            variation=self.variation,
        )
        self.flag.delete()
        self.assertEqual(TargetingRule.objects.count(), 0)
