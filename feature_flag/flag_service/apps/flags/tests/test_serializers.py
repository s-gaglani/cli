"""
Serializer-level tests for apps.flags.
"""
import uuid

from django.test import TestCase

from apps.flags.models import Flag
from apps.flags.serializers import (
    FlagCreateUpdateSerializer,
    FlagDetailSerializer,
    FlagListSerializer,
    VariationSerializer,
)


def _valid_flag_payload(**overrides):
    defaults = {
        "project_id": str(uuid.uuid4()),
        "environment_key": "production",
        "name": "My Flag",
        "key": "my-flag",
        "flag_type": "boolean",
        "is_enabled": False,
        "rollout_percentage": 50,
        "description": "A test flag",
        "tags": ["alpha", "beta"],
    }
    defaults.update(overrides)
    return defaults


class FlagCreateUpdateSerializerTest(TestCase):
    def test_valid_data(self):
        data = _valid_flag_payload()
        serializer = FlagCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rollout_percentage_zero(self):
        data = _valid_flag_payload(rollout_percentage=0)
        serializer = FlagCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rollout_percentage_100(self):
        data = _valid_flag_payload(rollout_percentage=100)
        serializer = FlagCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rollout_percentage_above_100_invalid(self):
        data = _valid_flag_payload(rollout_percentage=101)
        serializer = FlagCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rollout_percentage", serializer.errors)

    def test_rollout_percentage_negative_invalid(self):
        # PositiveSmallIntegerField already rejects negatives at field level
        data = _valid_flag_payload(rollout_percentage=-1)
        serializer = FlagCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_key_with_uppercase_invalid(self):
        data = _valid_flag_payload(key="InvalidKey")
        serializer = FlagCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("key", serializer.errors)

    def test_key_with_spaces_invalid(self):
        data = _valid_flag_payload(key="my flag key")
        serializer = FlagCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("key", serializer.errors)

    def test_key_with_hyphens_and_underscores_valid(self):
        data = _valid_flag_payload(key="my_flag-key-123")
        serializer = FlagCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_required_field(self):
        data = _valid_flag_payload()
        del data["name"]
        serializer = FlagCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_invalid_flag_type(self):
        data = _valid_flag_payload(flag_type="xml")
        serializer = FlagCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("flag_type", serializer.errors)


class FlagListSerializerTest(TestCase):
    def setUp(self):
        self.flag = Flag.objects.create(
            project_id=uuid.uuid4(),
            environment_key="production",
            name="List Flag",
            key="list-flag",
            flag_type="string",
            is_enabled=True,
            rollout_percentage=75,
        )

    def test_list_serializer_fields(self):
        serializer = FlagListSerializer(self.flag)
        data = serializer.data
        expected_fields = {
            "id",
            "project_id",
            "environment_key",
            "name",
            "key",
            "flag_type",
            "is_enabled",
            "rollout_percentage",
            "created_at",
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_list_serializer_excludes_description(self):
        serializer = FlagListSerializer(self.flag)
        self.assertNotIn("description", serializer.data)

    def test_list_serializer_excludes_variations(self):
        serializer = FlagListSerializer(self.flag)
        self.assertNotIn("variations", serializer.data)


class FlagDetailSerializerTest(TestCase):
    def setUp(self):
        self.flag = Flag.objects.create(
            project_id=uuid.uuid4(),
            environment_key="production",
            name="Detail Flag",
            key="detail-flag",
        )

    def test_detail_serializer_includes_variations(self):
        serializer = FlagDetailSerializer(self.flag)
        self.assertIn("variations", serializer.data)
        self.assertIsInstance(serializer.data["variations"], list)

    def test_detail_serializer_includes_targeting_rules_count(self):
        serializer = FlagDetailSerializer(self.flag)
        self.assertIn("targeting_rules_count", serializer.data)
        self.assertEqual(serializer.data["targeting_rules_count"], 0)

    def test_detail_serializer_includes_tags(self):
        serializer = FlagDetailSerializer(self.flag)
        self.assertIn("tags", serializer.data)


class VariationSerializerTest(TestCase):
    def setUp(self):
        self.flag = Flag.objects.create(
            project_id=uuid.uuid4(),
            environment_key="production",
            name="V Flag",
            key="v-flag",
        )

    def test_valid_variation(self):
        data = {
            "flag": str(self.flag.id),
            "name": "control",
            "value": {"enabled": False},
            "is_control": True,
        }
        serializer = VariationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_variation_missing_value(self):
        data = {
            "flag": str(self.flag.id),
            "name": "control",
            "is_control": True,
        }
        serializer = VariationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("value", serializer.errors)
