"""
Tests for evaluation app API views.
FlagServiceClient is mocked to isolate view logic from the external HTTP call.
"""
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.evaluation.models import EvaluationLog


EVALUATE_URL = '/api/v1/evaluate/'
EVALUATE_BULK_URL = '/api/v1/evaluate/bulk/'
LOGS_URL = '/api/v1/logs/'


def _flag(key='test-flag', is_enabled=True, rollout=100, flag_type='boolean', variations=None):
    """Helper to build a minimal flag dict."""
    return {
        'key': key,
        'is_enabled': is_enabled,
        'flag_type': flag_type,
        'rollout_percentage': rollout,
        'variations': variations or [],
    }


class EvaluateViewTest(TestCase):
    """Tests for POST /api/v1/evaluate/"""

    def setUp(self):
        self.client = APIClient()
        self.project_id = str(uuid.uuid4())
        self.payload = {
            'project_id': self.project_id,
            'environment_key': 'production',
            'flag_key': 'my-feature',
            'user_key': 'user-abc',
            'attributes': {'plan': 'premium'},
        }

    def _post(self, data=None, **kwargs):
        return self.client.post(
            EVALUATE_URL,
            data=data or self.payload,
            format='json',
            **kwargs,
        )

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_enabled_flag_returns_true(self, MockClient):
        MockClient.return_value.get_flag.return_value = _flag()
        response = self._post()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['value'])
        self.assertEqual(response.data['reason'], 'DEFAULT')
        self.assertEqual(response.data['flag_key'], 'my-feature')
        self.assertIn('evaluated_at', response.data)

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_disabled_flag_returns_false(self, MockClient):
        MockClient.return_value.get_flag.return_value = _flag(is_enabled=False)
        response = self._post()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['value'])
        self.assertEqual(response.data['reason'], 'DISABLED')

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_flag_not_found_returns_null(self, MockClient):
        MockClient.return_value.get_flag.return_value = None
        response = self._post()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['value'])
        self.assertEqual(response.data['reason'], 'FLAG_NOT_FOUND')

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_evaluation_log_is_created(self, MockClient):
        MockClient.return_value.get_flag.return_value = _flag()
        initial_count = EvaluationLog.objects.count()
        self._post()
        self.assertEqual(EvaluationLog.objects.count(), initial_count + 1)
        log = EvaluationLog.objects.latest('evaluated_at')
        self.assertEqual(log.flag_key, 'my-feature')
        self.assertEqual(log.user_key, 'user-abc')
        self.assertEqual(log.reason, 'DEFAULT')

    def test_missing_project_id_returns_400(self):
        data = dict(self.payload)
        del data['project_id']
        response = self._post(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('project_id', response.data)

    def test_invalid_project_id_returns_400(self):
        data = dict(self.payload, project_id='not-a-uuid')
        response = self._post(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_flag_key_returns_400(self):
        data = dict(self.payload)
        del data['flag_key']
        response = self._post(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_user_key_returns_400(self):
        data = dict(self.payload)
        del data['user_key']
        response = self._post(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_attributes_optional(self, MockClient):
        MockClient.return_value.get_flag.return_value = _flag()
        data = dict(self.payload)
        del data['attributes']
        response = self._post(data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_get_flag_called_with_correct_args(self, MockClient):
        MockClient.return_value.get_flag.return_value = _flag()
        self._post()
        MockClient.return_value.get_flag.assert_called_once()
        call_args = MockClient.return_value.get_flag.call_args
        # project_id, environment_key, flag_key
        self.assertEqual(str(call_args[0][1]), 'production')
        self.assertEqual(call_args[0][2], 'my-feature')

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_rollout_excluded_reason(self, MockClient):
        # 0% rollout excludes everyone
        MockClient.return_value.get_flag.return_value = _flag(rollout=0)
        response = self._post()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reason'], 'ROLLOUT_EXCLUDED')
        self.assertFalse(response.data['value'])


class EvaluateBulkViewTest(TestCase):
    """Tests for POST /api/v1/evaluate/bulk/"""

    def setUp(self):
        self.client = APIClient()
        self.project_id = str(uuid.uuid4())
        self.payload = {
            'project_id': self.project_id,
            'environment_key': 'staging',
            'user_key': 'user-bulk',
            'flag_keys': ['flag-a', 'flag-b'],
            'attributes': {},
        }

    def _post(self, data=None):
        return self.client.post(
            EVALUATE_BULK_URL,
            data=data or self.payload,
            format='json',
        )

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_bulk_returns_list(self, MockClient):
        MockClient.return_value.get_flags_bulk.return_value = [
            _flag(key='flag-a'),
            _flag(key='flag-b', is_enabled=False),
        ]
        response = self._post()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_bulk_result_contains_flag_keys(self, MockClient):
        MockClient.return_value.get_flags_bulk.return_value = [
            _flag(key='flag-a'),
            _flag(key='flag-b'),
        ]
        response = self._post()
        result_keys = {r['flag_key'] for r in response.data}
        self.assertEqual(result_keys, {'flag-a', 'flag-b'})

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_bulk_missing_flag_returns_flag_not_found(self, MockClient):
        # Only flag-a found; flag-b is missing
        MockClient.return_value.get_flags_bulk.return_value = [_flag(key='flag-a')]
        response = self._post()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reasons = {r['flag_key']: r['reason'] for r in response.data}
        self.assertEqual(reasons['flag-a'], 'DEFAULT')
        self.assertEqual(reasons['flag-b'], 'FLAG_NOT_FOUND')

    def test_empty_flag_keys_returns_400(self):
        data = dict(self.payload, flag_keys=[])
        response = self._post(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_user_key_returns_400(self):
        data = dict(self.payload)
        del data['user_key']
        response = self._post(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_bulk_creates_evaluation_logs(self, MockClient):
        MockClient.return_value.get_flags_bulk.return_value = [
            _flag(key='flag-a'),
            _flag(key='flag-b'),
        ]
        initial_count = EvaluationLog.objects.count()
        self._post()
        self.assertEqual(EvaluationLog.objects.count(), initial_count + 2)

    @patch('apps.evaluation.views.FlagServiceClient')
    def test_evaluated_at_present_in_each_result(self, MockClient):
        MockClient.return_value.get_flags_bulk.return_value = [_flag(key='flag-a')]
        response = self._post(data=dict(self.payload, flag_keys=['flag-a']))
        for item in response.data:
            self.assertIn('evaluated_at', item)


class EvaluationLogListViewTest(TestCase):
    """Tests for GET /api/v1/logs/"""

    def setUp(self):
        self.client = APIClient()
        self.project_id = uuid.uuid4()
        # Create some logs
        for i in range(5):
            EvaluationLog.objects.create(
                project_id=self.project_id,
                environment_key='production',
                flag_key=f'flag-{i}',
                user_key=f'user-{i}',
                result_value=True,
                reason='DEFAULT',
            )
        EvaluationLog.objects.create(
            project_id=self.project_id,
            environment_key='production',
            flag_key='flag-special',
            user_key='user-special',
            result_value=False,
            reason='DISABLED',
        )

    def test_list_returns_200(self):
        response = self.client.get(LOGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_returns_paginated_results(self):
        response = self.client.get(LOGS_URL)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

    def test_filter_by_project_id(self):
        other_project = uuid.uuid4()
        EvaluationLog.objects.create(
            project_id=other_project,
            environment_key='staging',
            flag_key='other-flag',
            user_key='user-other',
            result_value=True,
            reason='DEFAULT',
        )
        response = self.client.get(LOGS_URL, {'project_id': str(self.project_id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data['results']:
            self.assertEqual(item['project_id'], str(self.project_id))

    def test_filter_by_flag_key(self):
        response = self.client.get(LOGS_URL, {'flag_key': 'flag-special'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) >= 1)
        for item in response.data['results']:
            self.assertEqual(item['flag_key'], 'flag-special')

    def test_filter_by_reason(self):
        response = self.client.get(LOGS_URL, {'reason': 'DISABLED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data['results']:
            self.assertEqual(item['reason'], 'DISABLED')

    def test_filter_by_user_key(self):
        response = self.client.get(LOGS_URL, {'user_key': 'user-special'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data['results']:
            self.assertEqual(item['user_key'], 'user-special')


class HealthCheckViewTest(TestCase):
    """Tests for GET /health/"""

    def setUp(self):
        self.client = APIClient()

    def test_health_returns_200(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health_response_structure(self):
        response = self.client.get('/health/')
        data = response.json()
        self.assertEqual(data['service'], 'evaluation-service')
        self.assertEqual(data['version'], '1.0.0')
        self.assertIn('status', data)
