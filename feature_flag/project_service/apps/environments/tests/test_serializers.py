"""
Unit tests for Project and Environment serializers.
"""
from django.test import TestCase
from apps.organizations.models import Organization
from apps.environments.models import Project, Environment
from apps.environments.serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateUpdateSerializer,
    EnvironmentListSerializer,
    EnvironmentDetailSerializer,
    EnvironmentCreateUpdateSerializer,
)


class ProjectCreateUpdateSerializerTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Serial Org', slug='serial-org')

    def test_valid_data_is_valid(self):
        data = {
            'name': 'Valid Project',
            'slug': 'valid-project',
            'organization': str(self.org.id),
        }
        serializer = ProjectCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_name_invalid(self):
        data = {'slug': 'no-name', 'organization': str(self.org.id)}
        serializer = ProjectCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_missing_org_invalid(self):
        data = {'name': 'No Org', 'slug': 'no-org'}
        serializer = ProjectCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('organization', serializer.errors)

    def test_slug_normalised_to_lowercase(self):
        data = {'name': 'My Project', 'slug': 'My-Project', 'organization': str(self.org.id)}
        serializer = ProjectCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['slug'], 'my-project')

    def test_duplicate_slug_in_same_org_invalid(self):
        Project.objects.create(organization=self.org, name='Existing', slug='existing-slug')
        data = {
            'name': 'Duplicate',
            'slug': 'existing-slug',
            'organization': str(self.org.id),
        }
        serializer = ProjectCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class ProjectListSerializerTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='List Serial Org', slug='list-serial-org')
        self.project = Project.objects.create(
            organization=self.org,
            name='Listed Project',
            slug='listed-project',
        )

    def test_expected_fields_present(self):
        serializer = ProjectListSerializer(self.project)
        expected = {'id', 'name', 'slug', 'organization', 'is_active', 'created_at'}
        self.assertEqual(set(serializer.data.keys()), expected)


class ProjectDetailSerializerTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Detail Serial Org', slug='detail-serial-org')
        self.project = Project.objects.create(
            organization=self.org,
            name='Detail Project',
            slug='detail-project',
        )
        self.env = Environment.objects.create(
            project=self.project,
            name='Production',
            key='production',
        )

    def test_detail_serializer_has_environments(self):
        serializer = ProjectDetailSerializer(self.project)
        self.assertIn('environments', serializer.data)
        self.assertEqual(len(serializer.data['environments']), 1)

    def test_detail_serializer_has_environment_count(self):
        serializer = ProjectDetailSerializer(self.project)
        self.assertIn('environment_count', serializer.data)
        self.assertEqual(serializer.data['environment_count'], 1)


class EnvironmentCreateUpdateSerializerTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Env Serial Org', slug='env-serial-org')
        self.project = Project.objects.create(
            organization=self.org,
            name='Env Project',
            slug='env-project',
        )

    def test_valid_data_is_valid(self):
        data = {
            'name': 'Production',
            'key': 'production',
            'color': '#ef4444',
            'is_default': True,
            'project': str(self.project.id),
        }
        serializer = EnvironmentCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_color_raises_error(self):
        data = {
            'name': 'Bad Color',
            'key': 'bad-color',
            'color': 'red',
            'project': str(self.project.id),
        }
        serializer = EnvironmentCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('color', serializer.errors)

    def test_valid_short_hex_color(self):
        data = {
            'name': 'Short Color',
            'key': 'short-color',
            'color': '#fff',
            'project': str(self.project.id),
        }
        serializer = EnvironmentCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_project_invalid(self):
        data = {'name': 'No Project', 'key': 'no-project', 'color': '#fff'}
        serializer = EnvironmentCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('project', serializer.errors)

    def test_key_normalised_to_lowercase(self):
        data = {
            'name': 'Prod',
            'key': 'PRODUCTION',
            'color': '#6366f1',
            'project': str(self.project.id),
        }
        serializer = EnvironmentCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['key'], 'production')


class EnvironmentListSerializerTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='EL Org', slug='el-org')
        self.project = Project.objects.create(
            organization=self.org,
            name='EL Project',
            slug='el-project',
        )
        self.env = Environment.objects.create(
            project=self.project,
            name='Staging',
            key='staging',
        )

    def test_expected_fields_present(self):
        serializer = EnvironmentListSerializer(self.env)
        expected = {'id', 'name', 'key', 'color', 'is_default', 'created_at'}
        self.assertEqual(set(serializer.data.keys()), expected)
