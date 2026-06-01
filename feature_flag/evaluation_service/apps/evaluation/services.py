"""
Core flag evaluation logic for the evaluation service.
"""
import hashlib
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _get_user_bucket(user_key: str, flag_key: str) -> int:
    """
    Deterministically assign a user to a 0-99 bucket based on
    a hash of their user_key combined with the flag_key.
    This ensures consistent bucketing across evaluations.
    """
    raw = f"{user_key}:{flag_key}".encode("utf-8")
    hex_digest = hashlib.md5(raw).hexdigest()
    return int(hex_digest, 16) % 100


def evaluate_flag(
    flag_data: Optional[Dict[str, Any]],
    user_key: str,
    attributes: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluate a feature flag for a specific user.

    Args:
        flag_data: Flag configuration dict from flag_service, or None if not found.
        user_key: Unique identifier for the user being evaluated.
        attributes: Optional dict of user attributes (reserved for targeting rules).

    Returns:
        Dict with keys:
            - value: The resolved flag value (bool, str, int, etc.) or None.
            - reason: A string explaining why this value was returned.
    """
    if attributes is None:
        attributes = {}

    # Flag not found in flag_service
    if flag_data is None:
        return {"value": None, "reason": "FLAG_NOT_FOUND"}

    # Flag is globally disabled
    if not flag_data.get("is_enabled", False):
        return {"value": False, "reason": "DISABLED"}

    # Rollout percentage check
    rollout = flag_data.get("rollout_percentage", 100)
    try:
        rollout = int(rollout)
    except (TypeError, ValueError):
        rollout = 100

    if rollout < 100:
        bucket = _get_user_bucket(user_key, flag_data.get("key", ""))
        if bucket >= rollout:
            return {"value": False, "reason": "ROLLOUT_EXCLUDED"}

    # Determine the return value based on flag type
    flag_type = flag_data.get("flag_type", "boolean")
    variations = flag_data.get("variations", [])

    if flag_type == "boolean":
        return {"value": True, "reason": "DEFAULT"}

    # For multivariate flags, return the control variation value
    if variations:
        control = next(
            (v for v in variations if v.get("is_control", False)),
            None,
        )
        if control is not None:
            return {"value": control.get("value"), "reason": "DEFAULT"}

        # Fall back to first variation if no control is marked
        first = variations[0]
        return {"value": first.get("value"), "reason": "DEFAULT"}

    # Fallback for enabled flag with no variations
    return {"value": True, "reason": "DEFAULT"}


def evaluate_flags_bulk(
    flags_data: List[Optional[Dict[str, Any]]],
    flag_keys: List[str],
    user_key: str,
    attributes: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Evaluate multiple flags for a single user.

    Args:
        flags_data: List of flag configuration dicts (may be shorter than flag_keys
                    if some flags were not found).
        flag_keys: Ordered list of flag keys requested.
        user_key: Unique identifier for the user.
        attributes: Optional user attributes.

    Returns:
        List of evaluation result dicts, one per flag_key.
    """
    # Index fetched flags by their key for O(1) lookup
    flags_by_key: Dict[str, Dict] = {}
    for flag in flags_data:
        if flag and "key" in flag:
            flags_by_key[flag["key"]] = flag

    results = []
    for key in flag_keys:
        flag = flags_by_key.get(key)
        result = evaluate_flag(flag, user_key, attributes)
        result["flag_key"] = key
        results.append(result)

    return results
