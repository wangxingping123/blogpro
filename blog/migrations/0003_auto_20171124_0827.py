# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-24 00:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20171121_1717'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='articleup',
            unique_together=set([('article', 'user')]),
        ),
    ]