# Generated by Django 3.2.5 on 2021-08-18 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0017_auto_20210818_1952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='end_date',
            field=models.DateTimeField(default='2000-01-01 00:00:00'),
        ),
    ]
