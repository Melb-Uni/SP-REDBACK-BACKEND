# Generated by Django 3.0.6 on 2021-10-16 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('subject_id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('subject_code', models.CharField(db_column='subject_code', max_length=20, null=True, unique=True)),
                ('name', models.CharField(max_length=128, null=True)),
                ('coordinator_id', models.IntegerField()),
                ('create_date', models.BigIntegerField()),
                ('status', models.IntegerField()),
            ],
            options={
                'db_table': 'subject',
            },
        ),
    ]
