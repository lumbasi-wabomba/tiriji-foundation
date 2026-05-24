import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tiriji.settings')

app = Celery('tiriji')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()