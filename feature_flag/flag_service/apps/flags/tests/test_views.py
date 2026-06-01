"""
View-level (API) tests for apps.flags.
"""
import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.flags.models import Flag, TargetingRule, Variation


def _flag_data(**overrides):
    defaults = {
        "project_id": str(uuid.uuid4()),
        "environment_key": "production",
        "name": "Beta Feature",
        "key": "beta-feature",
        "flag_type": "boolean",
        "is_enabled": False,
        "rollout_percentage": 0,
        "description": "",
        "tags": [],
    }
    defaults.update(overrides)
    return defaults


class FlagListCreateViewTest(APITestCase):
    def test_list_flags_empty(self):
        url = reverse("flag-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_create_flag(self):
        url = reverse("flag-list")
        data = _flag_data()
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flag.objects.count(), 1)

    def test_create_flag_invalid_rollout(self):
        url = reverse("flag-list")
        data = _flag_data(rollout_percentage=150)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rollout_percentage", response.data)

    def test_create_flag_invalid_key(self):
        url = reverse("flag-list")
        data = _flag_data(key="Invalid Key!")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("key", response.data)

    def test_list_flags_pagination(self):
        project_id = uuid.uuid4()
        for i in range(25):
            Flag.objects.create(
                project_id=project_id,
                environment_key="production",
                name=f"Flag {i}",
                key=f"flag-{i}",
            )
        url = reverse("flag-list")
        response = self.client.get(url, {"page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["count"], 25)

    def test_filter_by_project_id(self):
        pid1 = uuid.uuid4()
        pid2 = uuid.uuid4()
        Flag.objects.create(
            project_id=pid1, environment_key="prod", name="F1", key="f1"
        )
        Flag.objects.create(
            project_id=pid2, environment_key="prod", name="F2", key="f2"
        )
        url = reverse("flag-list")
        response = self.client.get(url, {"project_id": str(pid1)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["key"], "f1")


class FlagDetailViewTest(APITestCase):
    def setUp(self):
        self.flag = Flag.objects.create(
            project_id=uuid.uuid4(),
            environment_key="production",
            name="Detail Flag",
            key="detail-flag",
        )

    def test_retrieve_flag(self):
        url = reverse("flag-detail", kwargs={"pk": str(self.flag.id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["key"], "detail-flag")
        self.assertIn("variations", response.data)
        self.assertIn("targeting_rules_count", response.data)

    def test_update_flag(self):
        url = reverse("flag-detail", kwargs={"pk": str(self.flag.id)})
        data = _flag_data(
            project_id=str(self.flag.project_id),
            environment_key=self.flag.environment_key,
            key=self.flag.key,
            name="Updated Name",
        )
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flag.refresh_from_db()
        self.assertEqual(self.flag.name, "Updated Name")

    def test_partial_update_flag(self):
        url = reverse("flag-detail", kwargs={"pk": str(self.flag.id)})
        response = self.client.patch(url, {"rollout_percentage": 50}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flag.refresh_from_db()
        self.assertEqual(self.flag.rollout_percentage, 50)

    def test_delete_flag(self):
        url = reverse("flag-detail", kwargs={"pk": str(self.flag.id)})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Flag.objects.filter(id=self.flag.id).exists())


class FlagToggleViewTest(APITestCase):
    def setUp(self):
        self.flag = Flag.objects.create(
            project_id=uuid.uuid4(),
            environment_key="production",
            name="Toggle Flag",
            key="toggle-flag",
            is_enabled=False,
        )

    def test_toggle_enables_flag(self):
        url = reverse("flag-toggle-flag", kwargs={"pk": str(self.flag.id)})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flag.refresh_from_db()
        self.assertTrue(self.flag.is_enabled)
        self.assertTrue(response.data["is_enabled"])

    def test_toggle_disables_flag(self):
        self.flag.is_enabled = True
        self.flag.save()
        url = reverse("flag-toggle-flag", kwargs={"pk": str(self.flag.id)})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flag.refresh_from_db()
        self.assertFalse(self.flag.is_enabled)

    def test_toggle_nonexistent_flag(self):
        url = reverse("flag-toggle-flag", kwargs={"pk": str(uuid.uuid4())})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VariationViewTest(APITestCase):
    def setUp(self):
        self.flag = Flag.objects.create(
            project_id=uuid.uuid4(),
            environment_key="production",
            name="Var Flag",
            key="var-flag",
        )

    def test_create_variation(self):
        url = reverse("variation-list")
        data = {
            "flag": str(self.flag.id),
            "name": "control",
            "value": False,
            "is_control": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Variation.objects.count(), 1)

    def test_list_variations(self):
        Variation.objects.create(flag=self.flag, name="ctrl", value=False)
        url = reverse("variation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class TargetingRuleViewTest(APITestCase):
    def setUp(self):
        self.flag = Flag.objects.create(
            project_id=uuid.uuid4(),
            environment_key="production",
            name="TR Flag",
            key="tr-flag",
        )
        self.variation = Variation.objects.create(
            flag=self.flag, name="on", value=True
        )

    def test_create_targeting_rule(self):
        url = reverse("targeting-rule-list")
        data = {
            "flag": str(self.flag.id),
            "segment_id": str(uuid.uuid4()),
            "variation": str(self.variation.id),
            "priority": 1,
            "is_active": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TargetingRule.objects.count(), 1)

    def test_list_targeting_rules(self):
        TargetingRule.objects.create(
            flag=self.flag,
            segment_id=uuid.uuid4(),
            variation=self.variation,
        )
        url = reverse("targeting-rule-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
