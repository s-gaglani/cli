"""
Integration tests for Project and Environment ViewSets.
"""
import json
from rest_framework import status
from rest_framework.test import APITestCase
from apps.organizations.models import Organization
from apps.environments.models import Project, Environment


class ProjectViewSetTest(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='View Org', slug='view-org')
        self.project = Project.objects.create(
            organization=self.org,
            name='Main Project',
            slug='main-project',
        )
        self.list_url = '/api/v1/projects/'
        self.detail_url = f'/api/v1/projects/{self.project.id}/'

    # --- List ---
    def test_list_returns_200(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_returns_paginated_results(self):
        response = self.client.get(self.list_url)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

    def test_list_contains_created_project(self):
        response = self.client.get(self.list_url)
        ids = [str(p['id']) for p in response.data['results']]
        self.assertIn(str(self.project.id), ids)

    # --- Create ---
    def test_create_returns_201(self):
        payload = {
            'name': 'New Project',
            'slug': 'new-project',
            'organization': str(self.org.id),
        }
        response = self.client.post(
            self.list_url,
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_with_duplicate_slug_in_same_org_returns_400(self):
        payload = {
            'name': 'Dup',
            'slug': 'main-project',
            'organization': str(self.org.id),
        }
        response = self.client.post(
            self.list_url,
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Retrieve ---
    def test_retrieve_returns_200(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_contains_environments_list(self):
        response = self.client.get(self.detail_url)
        self.assertIn('environments', response.data)

    # --- Update ---
    def test_partial_update_returns_200(self):
        response = self.client.patch(
            self.detail_url,
            data=json.dumps({'name': 'Updated Project'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Delete ---
    def test_delete_returns_204(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_removes_from_db(self):
        self.client.delete(self.detail_url)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    # --- Filtering ---
    def test_filter_by_organization(self):
        response = self.client.get(self.list_url, {'organization': str(self.org.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_by_name(self):
        response = self.client.get(self.list_url, {'search': 'Main'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [str(p['id']) for p in response.data['results']]
        self.assertIn(str(self.project.id), ids)


class EnvironmentViewSetTest(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Env View Org', slug='env-view-org')
        self.project = Project.objects.create(
            organization=self.org,
            name='Env Project',
            slug='env-project',
        )
        self.env = Environment.objects.create(
            project=self.project,
            name='Production',
            key='production',
        )
        self.list_url = '/api/v1/environments/'
        self.detail_url = f'/api/v1/environments/{self.env.id}/'

    def test_list_returns_200(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_contains_created_environment(self):
        response = self.client.get(self.list_url)
        ids = [str(e['id']) for e in response.data['results']]
        self.assertIn(str(self.env.id), ids)

    def test_create_returns_201(self):
        payload = {
            'name': 'Staging',
            'key': 'staging',
            'color': '#f59e0b',
            'is_default': False,
            'project': str(self.project.id),
        }
        response = self.client.post(
            self.list_url,
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_color_returns_400(self):
        payload = {
            'name': 'Bad Color',
            'key': 'bad-color',
            'color': 'not-a-color',
            'project': str(self.project.id),
        }
        response = self.client.post(
            self.list_url,
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_returns_200(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_returns_204(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_filter_by_project(self):
        response = self.client.get(self.list_url, {'project': str(self.project.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_is_default(self):
        response = self.client.get(self.list_url, {'is_default': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
