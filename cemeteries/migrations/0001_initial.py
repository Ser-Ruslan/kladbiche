# Generated by Django 5.1.6 on 2025-03-04 13:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cemetery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Coordinates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x_points', models.JSONField()),
                ('y_points', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CemeteryObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('GRAVE', 'Grave'), ('MONUMENT', 'Monument'), ('MEMORIAL', 'Memorial'), ('CHAPEL', 'Chapel'), ('OTHER', 'Other')], max_length=20)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('ARCHIVED', 'Archived'), ('PENDING_REVIEW', 'Pending Review'), ('DELETED', 'Deleted')], default='ACTIVE', max_length=20)),
                ('cemetery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cemeteries.cemetery')),
                ('coordinates', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='cemeteries.coordinates')),
            ],
        ),
    ]
