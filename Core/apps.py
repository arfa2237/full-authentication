#from django.apps import AppConfig


#class CoreConfig(AppConfig):
   # name = 'Core'
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Core'

    def ready(self):
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from django_apscheduler.jobstores import DjangoJobStore
            from Core.scheduler import send_appointment_reminders

            scheduler = BackgroundScheduler()
            scheduler.add_jobstore(DjangoJobStore(), "default")

            scheduler.add_job(
                send_appointment_reminders,
                trigger          = 'interval',
                minutes          = 5,
                id               = 'send_appointment_reminders',
                replace_existing = True,
                max_instances    = 1,
            )

            scheduler.start()
            print(" Reminder scheduler started successfully!")

        except Exception as e:
            print(f" Scheduler error: {e}")