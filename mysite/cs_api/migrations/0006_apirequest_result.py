# Generated by Django 3.2.7 on 2021-12-16 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cs_api', '0005_auto_20211216_2101'),
    ]

    operations = [
        migrations.AddField(
            model_name='apirequest',
            name='result',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
