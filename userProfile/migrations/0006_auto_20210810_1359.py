# Generated by Django 3.2.5 on 2021-08-10 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0005_alter_price_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='price',
        ),
        migrations.AddField(
            model_name='price',
            name='service',
            field=models.ForeignKey(default=0.0, on_delete=django.db.models.deletion.SET_DEFAULT, to='userProfile.service'),
        ),
    ]
