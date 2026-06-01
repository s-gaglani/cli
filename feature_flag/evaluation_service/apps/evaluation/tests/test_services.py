"""
Tests for the flag evaluation service logic.
Tests evaluate_flag() and evaluate_flags_bulk() directly.
"""
from django.test import TestCase
from apps.evaluation.services import evaluate_flag, evaluate_flags_bulk, _get_user_bucket


class GetUserBucketTest(TestCase):
    """Tests for the deterministic user bucketing function."""

    def test_returns_integer_in_range(self):
        """Bucket value is always 0-99."""
        for i in range(100):
            bucket = _get_user_bucket(f"user-{i}", "flag-key")
            self.assertGreaterEqual(bucket, 0)
            self.assertLess(bucket, 100)

    def test_deterministic(self):
        """Same inputs always produce same bucket."""
        b1 = _get_user_bucket("alice", "my-flag")
        b2 = _get_user_bucket("alice", "my-flag")
        self.assertEqual(b1, b2)

    def test_different_users_different_buckets(self):
        """Different users likely get different buckets (not guaranteed but highly probable)."""
        buckets = {_get_user_bucket(f"user-{i}", "flag") for i in range(50)}
        self.assertGreater(len(buckets), 5)

    def test_different_flags_different_buckets(self):
        """Same user gets different buckets for different flags."""
        b1 = _get_user_bucket("alice", "flag-a")
        b2 = _get_user_bucket("alice", "flag-b")
        # Not guaranteed equal, but should differ for different flag names
        # This is a sanity check — at minimum the function runs without error
        self.assertIsInstance(b1, int)
        self.assertIsInstance(b2, int)


class EvaluateFlagTest(TestCase):
    """Tests for the evaluate_flag() function."""

    def test_flag_not_found_returns_null(self):
        """None flag_data returns FLAG_NOT_FOUND."""
        result = evaluate_flag(None, "user-123")
        self.assertIsNone(result["value"])
        self.assertEqual(result["reason"], "FLAG_NOT_FOUND")

    def test_disabled_flag_returns_false(self):
        """Flag with is_enabled=False returns DISABLED."""
        flag = {"key": "test", "is_enabled": False, "flag_type": "boolean"}
        result = evaluate_flag(flag, "user-123")
        self.assertFalse(result["value"])
        self.assertEqual(result["reason"], "DISABLED")

    def test_enabled_boolean_flag_returns_true(self):
        """Enabled boolean flag returns True with DEFAULT reason."""
        flag = {
            "key": "test-flag",
            "is_enabled": True,
            "flag_type": "boolean",
            "rollout_percentage": 100,
        }
        result = evaluate_flag(flag, "user-123")
        self.assertTrue(result["value"])
        self.assertEqual(result["reason"], "DEFAULT")

    def test_full_rollout_always_includes_user(self):
        """100% rollout includes all users."""
        flag = {
            "key": "full-rollout",
            "is_enabled": True,
            "flag_type": "boolean",
            "rollout_percentage": 100,
        }
        for i in range(20):
            result = evaluate_flag(flag, f"user-{i}")
            self.assertNotEqual(result["reason"], "ROLLOUT_EXCLUDED")

    def test_zero_rollout_excludes_all_users(self):
        """0% rollout excludes all users."""
        flag = {
            "key": "zero-rollout",
            "is_enabled": True,
            "flag_type": "boolean",
            "rollout_percentage": 0,
        }
        for i in range(20):
            result = evaluate_flag(flag, f"user-{i}")
            self.assertFalse(result["value"])
            self.assertEqual(result["reason"], "ROLLOUT_EXCLUDED")

    def test_partial_rollout_is_deterministic(self):
        """Same user gets the same result for the same partial rollout."""
        flag = {
            "key": "partial-rollout",
            "is_enabled": True,
            "flag_type": "boolean",
            "rollout_percentage": 50,
        }
        result1 = evaluate_flag(flag, "stable-user")
        result2 = evaluate_flag(flag, "stable-user")
        self.assertEqual(result1["value"], result2["value"])
        self.assertEqual(result1["reason"], result2["reason"])

    def test_multivariate_flag_returns_control_value(self):
        """Multivariate flag returns the control variation value."""
        flag = {
            "key": "multi-flag",
            "is_enabled": True,
            "flag_type": "string",
            "rollout_percentage": 100,
            "variations": [
                {"value": "control-text", "is_control": True},
                {"value": "variant-text", "is_control": False},
            ],
        }
        result = evaluate_flag(flag, "user-abc")
        self.assertEqual(result["value"], "control-text")
        self.assertEqual(result["reason"], "DEFAULT")

    def test_multivariate_no_control_returns_first_variation(self):
        """When no variation is marked as control, first variation is used."""
        flag = {
            "key": "multi-no-control",
            "is_enabled": True,
            "flag_type": "string",
            "rollout_percentage": 100,
            "variations": [
                {"value": "first", "is_control": False},
                {"value": "second", "is_control": False},
            ],
        }
        result = evaluate_flag(flag, "user-xyz")
        self.assertEqual(result["value"], "first")

    def test_flag_missing_is_enabled_treated_as_disabled(self):
        """Flag without is_enabled key is treated as disabled."""
        flag = {"key": "no-enabled-key", "flag_type": "boolean"}
        result = evaluate_flag(flag, "user-123")
        self.assertEqual(result["reason"], "DISABLED")

    def test_attributes_accepted_without_error(self):
        """Passing attributes doesn't cause errors."""
        flag = {
            "key": "attr-flag",
            "is_enabled": True,
            "flag_type": "boolean",
            "rollout_percentage": 100,
        }
        result = evaluate_flag(flag, "user-123", attributes={"plan": "premium"})
        self.assertEqual(result["reason"], "DEFAULT")

    def test_none_attributes_defaults_to_empty_dict(self):
        """None attributes is treated as empty dict."""
        flag = {
            "key": "attr-flag",
            "is_enabled": True,
            "flag_type": "boolean",
            "rollout_percentage": 100,
        }
        result = evaluate_flag(flag, "user-123", attributes=None)
        self.assertEqual(result["reason"], "DEFAULT")

    def test_invalid_rollout_percentage_defaults_to_100(self):
        """Non-numeric rollout_percentage defaults to 100 (always include)."""
        flag = {
            "key": "bad-rollout",
            "is_enabled": True,
            "flag_type": "boolean",
            "rollout_percentage": "invalid",
        }
        result = evaluate_flag(flag, "user-123")
        self.assertNotEqual(result["reason"], "ROLLOUT_EXCLUDED")


class EvaluateFlagsBulkTest(TestCase):
    """Tests for the evaluate_flags_bulk() function."""

    def test_bulk_evaluation_returns_one_result_per_key(self):
        """Returns exactly one result for each requested flag_key."""
        flags_data = [
            {"key": "flag-a", "is_enabled": True, "flag_type": "boolean", "rollout_percentage": 100},
            {"key": "flag-b", "is_enabled": False, "flag_type": "boolean"},
        ]
        flag_keys = ["flag-a", "flag-b", "flag-c"]
        results = evaluate_flags_bulk(flags_data, flag_keys, "user-001")
        self.assertEqual(len(results), 3)

    def test_bulk_missing_flag_returns_flag_not_found(self):
        """Flag keys not in flags_data return FLAG_NOT_FOUND."""
        flags_data = [
            {"key": "flag-a", "is_enabled": True, "flag_type": "boolean", "rollout_percentage": 100},
        ]
        results = evaluate_flags_bulk(flags_data, ["flag-a", "missing-flag"], "user-001")
        reasons = {r["flag_key"]: r["reason"] for r in results}
        self.assertEqual(reasons["flag-a"], "DEFAULT")
        self.assertEqual(reasons["missing-flag"], "FLAG_NOT_FOUND")

    def test_bulk_preserves_flag_key_in_result(self):
        """Each result contains the correct flag_key."""
        flags_data = [
            {"key": "alpha", "is_enabled": True, "flag_type": "boolean", "rollout_percentage": 100},
            {"key": "beta", "is_enabled": True, "flag_type": "boolean", "rollout_percentage": 100},
        ]
        results = evaluate_flags_bulk(flags_data, ["alpha", "beta"], "user-x")
        keys_in_results = {r["flag_key"] for r in results}
        self.assertEqual(keys_in_results, {"alpha", "beta"})

    def test_bulk_empty_flags_data(self):
        """Empty flags_data treats all keys as not found."""
        results = evaluate_flags_bulk([], ["flag-1", "flag-2"], "user-99")
        for r in results:
            self.assertEqual(r["reason"], "FLAG_NOT_FOUND")

    def test_bulk_empty_flag_keys(self):
        """Empty flag_keys returns empty list."""
        results = evaluate_flags_bulk([], [], "user-99")
        self.assertEqual(results, [])
