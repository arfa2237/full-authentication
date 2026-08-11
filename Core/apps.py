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
        import os

        # Prevent running twice in development 

        if os.environ.get('RUN_MAIN') != 'true':
            return

        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.interval import IntervalTrigger
            from Core.scheduler import send_appointment_reminders

            scheduler = BackgroundScheduler()

            scheduler.add_job(
                send_appointment_reminders,
                trigger          = IntervalTrigger(minutes=5),
                id               = 'send_appointment_reminders',
                replace_existing = True,
                max_instances    = 1,
            )

            scheduler.start()
            print(" Reminder scheduler started successfully!")

        except Exception as e:
            print(f" Scheduler error: {e}")