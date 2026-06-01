"""
HTTP clients for communicating with external services.
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class FlagServiceClient:
    """
    Client for communicating with the flag_service.
    Fetches flag configuration data needed for evaluation.
    """

    def __init__(self):
        self.base_url = settings.FLAG_SERVICE_URL.rstrip('/')
        self.timeout = 2.0

    def get_flag(self, project_id, environment_key, flag_key):
        """
        Fetch a single flag configuration from flag_service.

        GET {flag_service}/api/v1/flags/?project_id=...&environment_key=...&key=...
        Returns the first matching flag dict, or None if not found/error.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/flags/",
                params={
                    "project_id": str(project_id),
                    "environment_key": environment_key,
                    "key": flag_key,
                },
                timeout=self.timeout,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            # Support both paginated ({"results": [...]}) and plain list responses
            results = data.get("results", data) if isinstance(data, dict) else data
            if isinstance(results, list) and results:
                return results[0]
            return None
        except requests.Timeout:
            logger.warning(
                "Timeout fetching flag %s from flag_service (project=%s, env=%s)",
                flag_key, project_id, environment_key,
            )
            return None
        except requests.ConnectionError:
            logger.error(
                "Connection error fetching flag %s from flag_service",
                flag_key,
            )
            return None
        except requests.HTTPError as exc:
            logger.warning(
                "HTTP error fetching flag %s: %s",
                flag_key, exc.response.status_code,
            )
            return None
        except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
            logger.exception("Unexpected error fetching flag %s: %s", flag_key, exc)
            return None

    def get_flags_bulk(self, project_id, environment_key, flag_keys):
        """
        Fetch multiple flag configurations from flag_service.
        Returns a list of flag dicts for flags that were found.
        """
        flags = []
        for key in flag_keys:
            flag = self.get_flag(project_id, environment_key, key)
            if flag is not None:
                flags.append(flag)
        return flags
