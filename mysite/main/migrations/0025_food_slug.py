# Generated by Django 2.2.6 on 2019-12-08 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20191208_0825'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='slug',
            field=models.SlugField(default=1),
            preserve_default=False,
        ),
    ]