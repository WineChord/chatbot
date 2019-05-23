"""Celery init."""
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the sefault Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mychat.settings')

app = Celery('mychat')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
