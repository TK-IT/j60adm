# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-20 12:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('j60adm', '0009_person_note'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='title',
            options={'ordering': ['-period', 'title']},
        ),
    ]
