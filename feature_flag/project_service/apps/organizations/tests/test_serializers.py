"""
Unit tests for Organization and APIKey serializers.
"""
from django.test import TestCase
from apps.organizations.models import Organization, APIKey
from apps.organizations.serializers import (
    OrganizationListSerializer,
    OrganizationDetailSerializer,
    OrganizationCreateUpdateSerializer,
    APIKeyListSerializer,
    APIKeyCreateSerializer,
    APIKeyDetailSerializer,
)


class OrganizationCreateUpdateSerializerTest(TestCase):
    def test_valid_data_is_valid(self):
        data = {'name': 'Valid Org', 'slug': 'valid-org', 'plan': 'free'}
        serializer = OrganizationCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_name_invalid(self):
        data = {'slug': 'no-name', 'plan': 'free'}
        serializer = OrganizationCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_missing_slug_invalid(self):
        data = {'name': 'No Slug', 'plan': 'free'}
        serializer = OrganizationCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('slug', serializer.errors)

    def test_invalid_plan_choice(self):
        data = {'name': 'Bad Plan', 'slug': 'bad-plan', 'plan': 'ultimate'}
        serializer = OrganizationCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('plan', serializer.errors)

    def test_slug_normalised_to_lowercase(self):
        data = {'name': 'Upper Org', 'slug': 'Upper-Org', 'plan': 'free'}
        serializer = OrganizationCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['slug'], 'upper-org')


class OrganizationListSerializerTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='List Org', slug='list-org', plan='pro')

    def test_serializer_contains_expected_fields(self):
        serializer = OrganizationListSerializer(self.org)
        expected = {'id', 'name', 'slug', 'plan', 'is_active', 'created_at'}
        self.assertEqual(set(serializer.data.keys()), expected)

    def test_serializer_id_is_string_uuid(self):
        serializer = OrganizationListSerializer(self.org)
        self.assertIsInstance(serializer.data['id'], str)


class OrganizationDetailSerializerTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Detail Org', slug='detail-org')

    def test_detail_serializer_has_project_count(self):
        serializer = OrganizationDetailSerializer(self.org)
        self.assertIn('project_count', serializer.data)

    def test_project_count_is_zero_initially(self):
        serializer = OrganizationDetailSerializer(self.org)
        self.assertEqual(serializer.data['project_count'], 0)


class APIKeyCreateSerializerTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Key Org', slug='key-org')

    def test_valid_data_is_valid(self):
        data = {
            'name': 'My Key',
            'key': 'a' * 64,
            'organization': str(self.org.id),
        }
        serializer = APIKeyCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_short_key_invalid(self):
        data = {
            'name': 'Short Key',
            'key': 'short',
            'organization': str(self.org.id),
        }
        serializer = APIKeyCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('key', serializer.errors)

    def test_missing_organization_invalid(self):
        data = {'name': 'No Org Key', 'key': 'a' * 32}
        serializer = APIKeyCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('organization', serializer.errors)


class APIKeyListSerializerTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Org', slug='org')
        self.key = APIKey.objects.create(
            organization=self.org,
            name='List Key',
            key='x' * 64,
        )

    def test_list_serializer_no_full_key_field(self):
        serializer = APIKeyListSerializer(self.key)
        self.assertNotIn('key', serializer.data)

    def test_list_serializer_has_prefix(self):
        serializer = APIKeyListSerializer(self.key)
        self.assertIn('prefix', serializer.data)
        self.assertEqual(serializer.data['prefix'], 'x' * 8)
