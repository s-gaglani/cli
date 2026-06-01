"""
Unit tests for Project and Environment models.
"""
import uuid
from django.test import TestCase
from apps.organizations.models import Organization
from apps.environments.models import Project, Environment


class ProjectModelTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Test Org', slug='test-org')
        self.project = Project.objects.create(
            organization=self.org,
            name='Web App',
            slug='web-app',
            description='Our main web application.',
        )

    def test_project_creation(self):
        """Project is created with correct field values."""
        self.assertIsInstance(self.project.id, uuid.UUID)
        self.assertEqual(self.project.name, 'Web App')
        self.assertEqual(self.project.slug, 'web-app')
        self.assertEqual(self.project.organization, self.org)
        self.assertTrue(self.project.is_active)

    def test_project_str(self):
        """__str__ includes project name and slugs."""
        result = str(self.project)
        self.assertIn('Web App', result)
        self.assertIn('web-app', result)

    def test_project_cascade_delete(self):
        """Deleting the organization also deletes its projects."""
        project_id = self.project.id
        self.org.delete()
        self.assertFalse(Project.objects.filter(id=project_id).exists())

    def test_project_unique_slug_per_org(self):
        """Two projects in the same org cannot share a slug."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Project.objects.create(
                organization=self.org,
                name='Duplicate',
                slug='web-app',
            )

    def test_project_same_slug_different_org(self):
        """Same slug is allowed across different organisations."""
        other_org = Organization.objects.create(name='Other Org', slug='other-org')
        p2 = Project.objects.create(
            organization=other_org,
            name='Web App',
            slug='web-app',
        )
        self.assertIsNotNone(p2.id)

    def test_project_timestamps_set(self):
        self.assertIsNotNone(self.project.created_at)
        self.assertIsNotNone(self.project.updated_at)


class EnvironmentModelTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Env Org', slug='env-org')
        self.project = Project.objects.create(
            organization=self.org,
            name='API Service',
            slug='api-service',
        )
        self.env = Environment.objects.create(
            project=self.project,
            name='Production',
            key='production',
            color='#ef4444',
            is_default=True,
        )

    def test_environment_creation(self):
        """Environment is created with correct field values."""
        self.assertIsInstance(self.env.id, uuid.UUID)
        self.assertEqual(self.env.name, 'Production')
        self.assertEqual(self.env.key, 'production')
        self.assertEqual(self.env.color, '#ef4444')
        self.assertTrue(self.env.is_default)

    def test_environment_str(self):
        """__str__ includes environment name, key, and project name."""
        result = str(self.env)
        self.assertIn('Production', result)
        self.assertIn('production', result)
        self.assertIn('API Service', result)

    def test_environment_cascade_delete(self):
        """Deleting the project also deletes its environments."""
        env_id = self.env.id
        self.project.delete()
        self.assertFalse(Environment.objects.filter(id=env_id).exists())

    def test_environment_unique_key_per_project(self):
        """Two environments in the same project cannot share a key."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Environment.objects.create(
                project=self.project,
                name='Prod Copy',
                key='production',
            )

    def test_environment_default_color(self):
        """Default color is #6366f1."""
        env = Environment.objects.create(
            project=self.project,
            name='Staging',
            key='staging',
        )
        self.assertEqual(env.color, '#6366f1')

    def test_environment_project_relation(self):
        """Environment is accessible via project.environments."""
        self.assertIn(self.env, self.project.environments.all())
