# Generated by Django 3.0.6 on 2021-05-07 09:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('jira', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='individualcontributions',
            name='space_key',
            field=models.CharField(default=django.utils.timezone.now, max_length=256),
            preserve_default=False,
        ),
    ]
