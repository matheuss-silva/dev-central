# Generated by Django 5.0.3 on 2025-02-06 03:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notificacoes', '0013_alter_event_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='notificacoes.event'),
        ),
    ]
