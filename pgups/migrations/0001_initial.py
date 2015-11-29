# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('typ', models.CharField(max_length=255)),
                ('date_start', models.DateField(db_index=True)),
                ('date_end', models.DateField(db_index=True)),
                ('finished', models.BooleanField()),
            ],
        ),
    ]
