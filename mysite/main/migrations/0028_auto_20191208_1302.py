# Generated by Django 2.2.6 on 2019-12-08 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_auto_20191208_1153'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='apartment_address',
        ),
        migrations.RemoveField(
            model_name='address',
            name='country',
        ),
        migrations.RemoveField(
            model_name='address',
            name='zip',
        ),
        migrations.AddField(
            model_name='address',
            name='phone_number',
            field=models.IntegerField(default=None),
            preserve_default=False,
        ),
    ]
