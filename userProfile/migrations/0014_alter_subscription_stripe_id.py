# Generated by Django 3.2.5 on 2021-08-18 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0013_alter_subscription_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='stripe_id',
            field=models.CharField(default='stripe id', max_length=256),
        ),
    ]