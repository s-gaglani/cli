"""
Unit tests for Organization and APIKey models.
"""
import uuid
from django.test import TestCase
from apps.organizations.models import Organization, APIKey


class OrganizationModelTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(
            name='Acme Corp',
            slug='acme-corp',
            plan='pro',
        )

    def test_organization_creation(self):
        """Organization is created with correct field values."""
        self.assertIsInstance(self.org.id, uuid.UUID)
        self.assertEqual(self.org.name, 'Acme Corp')
        self.assertEqual(self.org.slug, 'acme-corp')
        self.assertEqual(self.org.plan, 'pro')
        self.assertTrue(self.org.is_active)

    def test_organization_str(self):
        """__str__ returns name and slug."""
        self.assertIn('Acme Corp', str(self.org))
        self.assertIn('acme-corp', str(self.org))

    def test_organization_default_plan(self):
        """Default plan is 'free'."""
        org = Organization.objects.create(name='Free Org', slug='free-org')
        self.assertEqual(org.plan, 'free')

    def test_organization_slug_unique(self):
        """Duplicate slugs raise an IntegrityError."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Organization.objects.create(name='Other', slug='acme-corp')

    def test_organization_timestamps_set(self):
        """created_at and updated_at are populated automatically."""
        self.assertIsNotNone(self.org.created_at)
        self.assertIsNotNone(self.org.updated_at)


class APIKeyModelTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Test Org', slug='test-org')
        self.api_key = APIKey.objects.create(
            organization=self.org,
            name='Production Key',
            key='abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
        )

    def test_apikey_creation(self):
        """APIKey is created with correct field values."""
        self.assertIsInstance(self.api_key.id, uuid.UUID)
        self.assertEqual(self.api_key.name, 'Production Key')
        self.assertTrue(self.api_key.is_active)

    def test_apikey_prefix_set_on_save(self):
        """prefix is automatically populated from the first 8 chars of key."""
        self.assertEqual(self.api_key.prefix, 'abcdef12')

    def test_apikey_str(self):
        """__str__ includes the key name and prefix."""
        result = str(self.api_key)
        self.assertIn('Production Key', result)
        self.assertIn('abcdef12', result)

    def test_apikey_cascade_delete(self):
        """Deleting the organization also deletes its API keys."""
        key_id = self.api_key.id
        self.org.delete()
        self.assertFalse(APIKey.objects.filter(id=key_id).exists())

    def test_apikey_organization_relation(self):
        """API key is accessible via organization.api_keys."""
        self.assertIn(self.api_key, self.org.api_keys.all())
