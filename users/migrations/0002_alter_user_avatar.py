# Generated by Django 4.2.16 on 2024-12-25 14:07

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, help_text='User avatar', null=True, upload_to=users.models.avatar_upload_path),
        ),
    ]
