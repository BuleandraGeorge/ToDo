# Generated by Django 3.2.5 on 2021-08-31 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0028_auto_20210831_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='stripe_id',
            field=models.CharField(editable=False, max_length=256),
        ),
    ]
