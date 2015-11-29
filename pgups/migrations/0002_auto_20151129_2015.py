# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pgups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Age',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('min_age', models.PositiveSmallIntegerField()),
                ('max_age', models.PositiveSmallIntegerField()),
                ('relay', models.BooleanField()),
                ('kids', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Competitor',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('approved', models.BooleanField()),
                ('age', models.ForeignKey(to='pgups.Age')),
            ],
        ),
        migrations.CreateModel(
            name='Distance',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('meters', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('lane', models.PositiveIntegerField()),
                ('competitor', models.ForeignKey(to='pgups.Competitor')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('birth_year', models.PositiveSmallIntegerField()),
                ('gender', models.BooleanField()),
                ('reg_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('representative', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('ip', models.GenericIPAddressField()),
                ('date', models.DateTimeField(auto_now=True)),
                ('competition', models.ForeignKey(to='pgups.Competition')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('time', models.DecimalField(decimal_places=3, max_digits=7)),
                ('result', models.PositiveSmallIntegerField()),
                ('points', models.PositiveSmallIntegerField()),
                ('competitor', models.ForeignKey(to='pgups.Competitor')),
            ],
        ),
        migrations.CreateModel(
            name='Start',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('competitors', models.ManyToManyField(to='pgups.Competitor', related_name='in_starts', through='pgups.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('active', models.BooleanField()),
                ('reg_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('gender', models.BooleanField()),
                ('finished', models.BooleanField()),
                ('age', models.ForeignKey(to='pgups.Age')),
                ('competition', models.ForeignKey(to='pgups.Competition')),
                ('distance', models.ForeignKey(to='pgups.Distance')),
                ('style', models.ForeignKey(to='pgups.Style')),
            ],
        ),
        migrations.AddField(
            model_name='result',
            name='tour',
            field=models.ForeignKey(to='pgups.Tour'),
        ),
        migrations.AddField(
            model_name='request',
            name='team',
            field=models.ForeignKey(to='pgups.Team'),
        ),
        migrations.AddField(
            model_name='order',
            name='start',
            field=models.ForeignKey(to='pgups.Start'),
        ),
        migrations.AddField(
            model_name='competitor',
            name='person',
            field=models.ForeignKey(to='pgups.Person'),
        ),
        migrations.AddField(
            model_name='competitor',
            name='request',
            field=models.ForeignKey(to='pgups.Request'),
        ),
        migrations.AddField(
            model_name='competitor',
            name='tour',
            field=models.ForeignKey(to='pgups.Tour'),
        ),
    ]
