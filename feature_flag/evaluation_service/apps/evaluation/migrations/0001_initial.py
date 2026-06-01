"""
Initial migration for the evaluation app.
Creates the EvaluationLog table.
"""
import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='EvaluationLog',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False,
                )),
                ('project_id', models.UUIDField(db_index=True)),
                ('environment_key', models.CharField(db_index=True, max_length=50)),
                ('flag_key', models.CharField(db_index=True, max_length=100)),
                ('user_key', models.CharField(db_index=True, max_length=255)),
                ('result_value', models.JSONField()),
                ('reason', models.CharField(
                    choices=[
                        ('DEFAULT', 'Default'),
                        ('TARGETING', 'Targeting'),
                        ('ROLLOUT', 'Rollout'),
                        ('DISABLED', 'Disabled'),
                        ('ROLLOUT_EXCLUDED', 'Rollout Excluded'),
                        ('FLAG_NOT_FOUND', 'Flag Not Found'),
                    ],
                    default='DEFAULT',
                    max_length=50,
                )),
                ('evaluated_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Evaluation Log',
                'verbose_name_plural': 'Evaluation Logs',
                'ordering': ['-evaluated_at'],
            },
        ),
        migrations.AddIndex(
            model_name='evaluationlog',
            index=models.Index(
                fields=['project_id', 'environment_key', 'flag_key'],
                name='evaluation_project_env_flag_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='evaluationlog',
            index=models.Index(
                fields=['user_key', 'evaluated_at'],
                name='evaluation_user_key_at_idx',
            ),
        ),
    ]
