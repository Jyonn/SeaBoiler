# Generated by Django 2.0 on 2018-10-17 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=64)),
                ('avatar', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('nickname', models.CharField(blank=True, default=None, max_length=64, null=True)),
            ],
        ),
    ]