# Generated by Django 3.2.5 on 2021-08-31 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0024_profile_stripe_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='stripe_id',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
