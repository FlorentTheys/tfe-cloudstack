# Generated by Django 3.2.7 on 2021-12-15 21:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cs_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='command',
            name='doc_url',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='command',
            name='category_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='command_ids', to='cs_api.category'),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='command_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='parameter_ids', to='cs_api.command'),
        ),
    ]
