# Generated by Django 4.2.16 on 2024-12-21 19:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_alter_history_object_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
