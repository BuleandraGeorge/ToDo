# Generated by Django 3.2.5 on 2021-08-19 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0018_alter_subscription_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='end_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='start_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
