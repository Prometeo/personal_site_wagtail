# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-16 21:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0017_auto_20170516_2101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogindexpage',
            name='intro',
        ),
    ]
