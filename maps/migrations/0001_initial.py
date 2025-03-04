# Generated by Django 5.1.6 on 2025-03-04 13:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cemeteries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boundaries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('north_east', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='north_east_boundary', to='cemeteries.coordinates')),
                ('south_west', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='south_west_boundary', to='cemeteries.coordinates')),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scale', models.FloatField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('boundaries', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='maps.boundaries')),
                ('cemetery', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='cemeteries.cemetery')),
            ],
        ),
        migrations.CreateModel(
            name='MapLayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('BASE', 'Base'), ('GRAVES', 'Graves'), ('MONUMENTS', 'Monuments'), ('INFRASTRUCTURE', 'Infrastructure'), ('PATHS', 'Paths'), ('VEGETATION', 'Vegetation'), ('CUSTOM', 'Custom')], max_length=20)),
                ('visible', models.BooleanField(default=True)),
                ('opacity', models.FloatField(default=1.0)),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='layers', to='maps.map')),
                ('objects', models.ManyToManyField(to='cemeteries.cemeteryobject')),
            ],
        ),
    ]
