# Generated by Django 3.2.5 on 2021-08-31 16:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0029_alter_profile_stripe_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='description',
            new_name='content',
        ),
    ]
