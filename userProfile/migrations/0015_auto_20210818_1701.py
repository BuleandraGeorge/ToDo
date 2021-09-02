# Generated by Django 3.2.5 on 2021-08-18 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0014_alter_subscription_stripe_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='period',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='start_date',
            field=models.DateField(default='2000-01-01'),
        ),
    ]
