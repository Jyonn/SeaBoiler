# Generated by Django 2.0 on 2018-10-17 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0002_user_str_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reviewer',
            field=models.BooleanField(default=False),
        ),
    ]