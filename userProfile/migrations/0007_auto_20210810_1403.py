# Generated by Django 3.2.5 on 2021-08-10 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0006_auto_20210810_1359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='price',
            name='service',
        ),
        migrations.AddField(
            model_name='service',
            name='price',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='userProfile.price'),
            preserve_default=False,
        ),
    ]