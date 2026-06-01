"""
AppConfig for the evaluation app.
"""
from django.apps import AppConfig


class EvaluationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.evaluation'
    label = 'evaluation'
    verbose_name = 'Evaluation'

    def ready(self):
        """Perform initialization tasks when the app is ready."""
        pass
