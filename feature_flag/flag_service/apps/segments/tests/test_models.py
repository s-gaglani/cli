"""
Model-level tests for apps.segments.
"""
import uuid

from django.test import TestCase

from apps.segments.models import Segment


class SegmentModelTest(TestCase):
    def _make_segment(self, **kwargs) -> Segment:
        defaults = {
            "project_id": uuid.uuid4(),
            "name": "Beta Users",
            "description": "Users opted into the beta programme",
            "rules": [
                {"attribute": "plan", "operator": "in", "value": ["pro", "enterprise"]}
            ],
        }
        defaults.update(kwargs)
        return Segment.objects.create(**defaults)

    def test_create_segment_defaults(self):
        segment = self._make_segment()
        self.assertIsNotNone(segment.id)
        self.assertIsNotNone(segment.created_at)
        self.assertIsNotNone(segment.updated_at)

    def test_segment_str(self):
        segment = self._make_segment(name="Power Users")
        self.assertIn("Power Users", str(segment))

    def test_segment_rules_default_list(self):
        segment = Segment.objects.create(
            project_id=uuid.uuid4(), name="Empty Rules"
        )
        self.assertEqual(segment.rules, [])

    def test_segment_rules_stored_and_retrieved(self):
        rules = [
            {"attribute": "country", "operator": "eq", "value": "US"},
            {"attribute": "age", "operator": "gte", "value": 18},
        ]
        segment = self._make_segment(rules=rules)
        segment.refresh_from_db()
        self.assertEqual(segment.rules, rules)

    def test_segment_ordering_newest_first(self):
        pid = uuid.uuid4()
        s1 = self._make_segment(project_id=pid, name="First")
        s2 = self._make_segment(project_id=pid, name="Second")
        segments = list(Segment.objects.filter(project_id=pid))
        self.assertEqual(segments[0].id, s2.id)
        self.assertEqual(segments[1].id, s1.id)

    def test_segment_update_changes_updated_at(self):
        segment = self._make_segment()
        original_updated_at = segment.updated_at
        segment.name = "Updated Name"
        segment.save()
        segment.refresh_from_db()
        self.assertGreaterEqual(segment.updated_at, original_updated_at)
        self.assertEqual(segment.name, "Updated Name")
