"""
Integration tests for Organization and APIKey ViewSets.
"""
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.organizations.models import Organization, APIKey


class OrganizationViewSetTest(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(
            name='Acme Corp',
            slug='acme-corp',
            plan='pro',
        )
        self.list_url = '/api/v1/organizations/'
        self.detail_url = f'/api/v1/organizations/{self.org.id}/'

    # --- List ---
    def test_list_returns_200(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_returns_results_key(self):
        response = self.client.get(self.list_url)
        self.assertIn('results', response.data)

    def test_list_contains_created_org(self):
        response = self.client.get(self.list_url)
        ids = [str(o['id']) for o in response.data['results']]
        self.assertIn(str(self.org.id), ids)

    # --- Create ---
    def test_create_returns_201(self):
        payload = {'name': 'New Org', 'slug': 'new-org', 'plan': 'free'}
        response = self.client.post(
            self.list_url, data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_persists_to_db(self):
        payload = {'name': 'Persisted Org', 'slug': 'persisted-org', 'plan': 'enterprise'}
        self.client.post(self.list_url, data=json.dumps(payload), content_type='application/json')
        self.assertTrue(Organization.objects.filter(slug='persisted-org').exists())

    def test_create_duplicate_slug_returns_400(self):
        payload = {'name': 'Duplicate', 'slug': 'acme-corp', 'plan': 'free'}
        response = self.client.post(
            self.list_url, data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Retrieve ---
    def test_retrieve_returns_200(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_returns_project_count(self):
        response = self.client.get(self.detail_url)
        self.assertIn('project_count', response.data)

    # --- Update ---
    def test_partial_update_returns_200(self):
        response = self.client.patch(
            self.detail_url,
            data=json.dumps({'name': 'Acme Updated'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Delete ---
    def test_delete_returns_204(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_removes_from_db(self):
        self.client.delete(self.detail_url)
        self.assertFalse(Organization.objects.filter(id=self.org.id).exists())


class APIKeyViewSetTest(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Key Org', slug='key-org')
        self.api_key = APIKey.objects.create(
            organization=self.org,
            name='Test Key',
            key='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',  # 64 chars
        )
        self.list_url = '/api/v1/api-keys/'
        self.detail_url = f'/api/v1/api-keys/{self.api_key.id}/'

    def test_list_returns_200(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_does_not_expose_full_key(self):
        response = self.client.get(self.list_url)
        for item in response.data['results']:
            self.assertNotIn('key', item)

    def test_create_returns_201(self):
        payload = {
            'name': 'New Key',
            'key': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            'organization': str(self.org.id),
        }
        response = self.client.post(
            self.list_url, data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_returns_200(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_returns_204(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
