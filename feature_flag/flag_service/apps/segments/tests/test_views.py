"""
View-level (API) tests for apps.segments.
"""
import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.segments.models import Segment


def _segment_data(**overrides):
    defaults = {
        "project_id": str(uuid.uuid4()),
        "name": "Beta Users",
        "description": "Beta programme participants",
        "rules": [
            {"attribute": "plan", "operator": "in", "value": ["pro", "enterprise"]}
        ],
    }
    defaults.update(overrides)
    return defaults


class SegmentListCreateViewTest(APITestCase):
    def test_list_segments_empty(self):
        url = reverse("segment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_create_segment(self):
        url = reverse("segment-list")
        data = _segment_data()
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Segment.objects.count(), 1)

    def test_create_segment_with_empty_rules(self):
        url = reverse("segment-list")
        data = _segment_data(rules=[])
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_segment_invalid_rules_not_list(self):
        url = reverse("segment-list")
        data = _segment_data(rules={"attribute": "country"})
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rules", response.data)

    def test_create_segment_invalid_rules_missing_key(self):
        url = reverse("segment-list")
        data = _segment_data(rules=[{"attribute": "country", "operator": "eq"}])  # missing value
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_segment_invalid_operator(self):
        url = reverse("segment-list")
        data = _segment_data(
            rules=[{"attribute": "country", "operator": "startswith", "value": "U"}]
        )
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rules", response.data)

    def test_list_segments_pagination(self):
        pid = uuid.uuid4()
        for i in range(25):
            Segment.objects.create(
                project_id=pid,
                name=f"Segment {i}",
            )
        url = reverse("segment-list")
        response = self.client.get(url, {"page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["count"], 25)

    def test_filter_by_project_id(self):
        pid1 = uuid.uuid4()
        pid2 = uuid.uuid4()
        Segment.objects.create(project_id=pid1, name="S1")
        Segment.objects.create(project_id=pid2, name="S2")
        url = reverse("segment-list")
        response = self.client.get(url, {"project_id": str(pid1)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "S1")


class SegmentDetailViewTest(APITestCase):
    def setUp(self):
        self.segment = Segment.objects.create(
            project_id=uuid.uuid4(),
            name="Detail Segment",
            description="A segment for testing",
            rules=[{"attribute": "plan", "operator": "eq", "value": "pro"}],
        )

    def test_retrieve_segment(self):
        url = reverse("segment-detail", kwargs={"pk": str(self.segment.id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Detail Segment")
        self.assertIn("rules", response.data)

    def test_update_segment(self):
        url = reverse("segment-detail", kwargs={"pk": str(self.segment.id)})
        data = _segment_data(
            project_id=str(self.segment.project_id),
            name="Updated Segment",
        )
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.segment.refresh_from_db()
        self.assertEqual(self.segment.name, "Updated Segment")

    def test_partial_update_segment(self):
        url = reverse("segment-detail", kwargs={"pk": str(self.segment.id)})
        response = self.client.patch(
            url, {"description": "patched description"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.segment.refresh_from_db()
        self.assertEqual(self.segment.description, "patched description")

    def test_delete_segment(self):
        url = reverse("segment-detail", kwargs={"pk": str(self.segment.id)})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Segment.objects.filter(id=self.segment.id).exists())

    def test_retrieve_nonexistent_segment(self):
        url = reverse("segment-detail", kwargs={"pk": str(uuid.uuid4())})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
