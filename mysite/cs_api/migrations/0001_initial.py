# Generated by Django 3.2.7 on 2021-11-06 14:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APIRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Command',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category_id', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='cs_api.category')),
            ],
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('required', models.BooleanField()),
                ('command_id', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='cs_api.command')),
            ],
        ),
        migrations.CreateModel(
            name='APIRequestParameterValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=500)),
                ('parameter_id', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='cs_api.parameter')),
                ('request_id', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='value_ids', to='cs_api.apirequest')),
            ],
        ),
        migrations.AddField(
            model_name='apirequest',
            name='command_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='cs_api.command'),
        ),
    ]
