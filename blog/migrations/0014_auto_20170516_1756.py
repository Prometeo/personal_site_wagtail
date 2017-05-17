# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-16 17:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0019_delete_filter'),
        ('blog', '0013_remove_blogindexpage_header_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogindexpage',
            name='description',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name='blogindexpage',
            name='header_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
    ]