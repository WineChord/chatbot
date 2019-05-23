"""Initialize celery."""
from __future__ import absolute_import, unicode_literals
# This imports the app object we created in celery.py as celery_app once the app is loaded
from .celery import app as celery_app

__all__ = ['celery_app']
