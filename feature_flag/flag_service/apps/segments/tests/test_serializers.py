"""
Serializer-level tests for apps.segments.
"""
import uuid

from django.test import TestCase

from apps.segments.models import Segment
from apps.segments.serializers import (
    SegmentCreateUpdateSerializer,
    SegmentDetailSerializer,
    SegmentListSerializer,
)


def _valid_segment_payload(**overrides):
    defaults = {
        "project_id": str(uuid.uuid4()),
        "name": "Power Users",
        "description": "Users on the power plan",
        "rules": [
            {"attribute": "plan", "operator": "eq", "value": "power"},
        ],
    }
    defaults.update(overrides)
    return defaults


class SegmentCreateUpdateSerializerTest(TestCase):
    def test_valid_data(self):
        data = _valid_segment_payload()
        serializer = SegmentCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_valid_empty_rules(self):
        data = _valid_segment_payload(rules=[])
        serializer = SegmentCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_rules_not_list(self):
        data = _valid_segment_payload(rules="not a list")
        serializer = SegmentCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rules", serializer.errors)

    def test_invalid_rule_not_dict(self):
        data = _valid_segment_payload(rules=["not a dict"])
        serializer = SegmentCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rules", serializer.errors)

    def test_invalid_rule_missing_attribute(self):
        data = _valid_segment_payload(
            rules=[{"operator": "eq", "value": "us"}]  # missing attribute
        )
        serializer = SegmentCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rules", serializer.errors)

    def test_invalid_rule_missing_operator(self):
        data = _valid_segment_payload(
            rules=[{"attribute": "country", "value": "us"}]
        )
        serializer = SegmentCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rules", serializer.errors)

    def test_invalid_rule_missing_value(self):
        data = _valid_segment_payload(
            rules=[{"attribute": "country", "operator": "eq"}]
        )
        serializer = SegmentCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rules", serializer.errors)

    def test_invalid_operator(self):
        data = _valid_segment_payload(
            rules=[{"attribute": "country", "operator": "startswith", "value": "U"}]
        )
        serializer = SegmentCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("rules", serializer.errors)

    def test_all_valid_operators(self):
        valid_operators = [
            "eq", "neq", "in", "not_in",
            "contains", "not_contains",
            "gt", "gte", "lt", "lte",
        ]
        for op in valid_operators:
            data = _valid_segment_payload(
                rules=[{"attribute": "score", "operator": op, "value": 10}]
            )
            serializer = SegmentCreateUpdateSerializer(data=data)
            self.assertTrue(
                serializer.is_valid(),
                f"Operator '{op}' should be valid. Errors: {serializer.errors}",
            )

    def test_missing_required_name(self):
        data = _valid_segment_payload()
        del data["name"]
        serializer = SegmentCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_multiple_rules_valid(self):
        data = _valid_segment_payload(
            rules=[
                {"attribute": "country", "operator": "eq", "value": "US"},
                {"attribute": "plan", "operator": "in", "value": ["pro", "enterprise"]},
                {"attribute": "age", "operator": "gte", "value": 18},
            ]
        )
        serializer = SegmentCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class SegmentListSerializerTest(TestCase):
    def setUp(self):
        self.segment = Segment.objects.create(
            project_id=uuid.uuid4(),
            name="List Segment",
            description="For listing",
            rules=[],
        )

    def test_list_serializer_fields(self):
        serializer = SegmentListSerializer(self.segment)
        data = serializer.data
        expected_fields = {"id", "project_id", "name", "description", "created_at"}
        self.assertEqual(set(data.keys()), expected_fields)

    def test_list_serializer_excludes_rules(self):
        serializer = SegmentListSerializer(self.segment)
        self.assertNotIn("rules", serializer.data)


class SegmentDetailSerializerTest(TestCase):
    def setUp(self):
        self.segment = Segment.objects.create(
            project_id=uuid.uuid4(),
            name="Detail Segment",
            description="For detail",
            rules=[{"attribute": "plan", "operator": "eq", "value": "pro"}],
        )

    def test_detail_serializer_includes_rules(self):
        serializer = SegmentDetailSerializer(self.segment)
        self.assertIn("rules", serializer.data)
        self.assertIsInstance(serializer.data["rules"], list)

    def test_detail_serializer_includes_updated_at(self):
        serializer = SegmentDetailSerializer(self.segment)
        self.assertIn("updated_at", serializer.data)
