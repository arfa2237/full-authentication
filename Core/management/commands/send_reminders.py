from django.core.management.base import BaseCommand
from Core.scheduler import send_appointment_reminders


class Command(BaseCommand):
    help = 'Send 30 Minute appointment reminder emails'

    def handle(self, *args, **kwargs):
        self.stdout.write('Checking appointment reminders...')
        send_appointment_reminders()
        self.stdout.write(
            self.style.SUCCESS('Reminder check complete!')
        )