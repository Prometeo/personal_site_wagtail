# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-16 15:50
from __future__ import unicode_literals

from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20170516_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='categories',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='blog.PostCategory'),
        ),
    ]