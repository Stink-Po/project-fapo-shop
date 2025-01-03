from __future__ import absolute_import, unicode_literals

from django.conf import settings

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fapo.settings')

app = Celery('fapo')

# Ensure that Celery discovers the tasks in the 'orders' app
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
