# Generated by Django 3.0.8 on 2020-08-15 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_manager', '0002_auto_20200815_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='tags',
            field=models.ManyToManyField(blank=True, to='task_manager.Tag'),
        ),
    ]
