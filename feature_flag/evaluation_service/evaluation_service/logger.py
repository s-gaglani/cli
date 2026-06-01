"""
Centralized logger configuration for evaluation_service.
"""
import logging


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for use throughout the application.

    Usage:
        from evaluation_service.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Flag evaluated", extra={"flag_key": "my-flag"})
    """
    return logging.getLogger(name)


# Module-level loggers for common use
evaluation_logger = get_logger('apps.evaluation')
client_logger = get_logger('apps.evaluation.clients')
service_logger = get_logger('apps.evaluation.services')
