# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-11 17:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('j60adm', '0002_rename_recipient_str'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailmessage',
            name='recipient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='j60adm.EmailAddress'),
        ),
    ]
