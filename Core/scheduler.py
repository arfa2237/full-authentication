import datetime
import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_appointment_reminders():
    """
    Checks for appointments in next 25-35 minutes
    and sends reminder emails.
    Called every 5 minutes via Railway Cron Job.
    """
    from Core.models import Appointment

    # Get current Pakistan time
    now      = timezone.localtime(timezone.now())
    today    = now.date()
    now_time = now.time()

    print(f"Reminder check at {now_time} | Date: {today}")
    logger.info(f"Reminder check at {now_time}")

    # Calculate 30 minute window (25 to 35 minutes ahead)
    now_dt       = datetime.datetime.combine(today, now_time)
    window_start = (now_dt + timedelta(minutes=25)).time()
    window_end   = (now_dt + timedelta(minutes=35)).time()

    print(f"Window: {window_start} → {window_end}")

    # Find matching appointments
    upcoming = Appointment.objects.filter(
        appointment_date      = today,
        status__in            = ['scheduled', 'pending'],
        reminder_sent         = False,
        appointment_time__gte = window_start,
        appointment_time__lte = window_end,
    )

    count = upcoming.count()
    print(f"Found {count} appointments to remind")

    if count == 0:
        print("No reminders needed right now")
        return

    for appt in upcoming:
        patient_email = appt.patient.email
        patient_name  = (
            appt.patient.get_full_name() or
            appt.patient.username
        )
        child_name    = appt.child_name or patient_name
        vaccine       = appt.vaccine_type
        appt_time_str = appt.appointment_time.strftime("%I:%M %p")
        appt_date_str = appt.appointment_date.strftime(
            "%A, %d %B %Y"
        )
        center_name   = (
            appt.center.name
            if appt.center
            else "your vaccination center"
        )

        if not patient_email:
            print(f"No email for {patient_name} — skipping")
            continue

        subject = f'TIG Reminder — {vaccine} in 30 Minutes!'
        body = (
            f'Dear {patient_name},\n\n'
            f'APPOINTMENT REMINDER\n\n'
            f'Your child\'s vaccination appointment\n'
            f'is scheduled in approximately 30 MINUTES!\n\n'
            f'--------------------------------------\n'
            f'APPOINTMENT DETAILS\n'
            f'-------------------------------\n'
            f'  Patient (Child) : {child_name}\n'
            f'  Vaccine         : {vaccine}\n'
            f'  Dose Number     : {appt.dose_number}\n'
            f'  Date            : {appt_date_str}\n'
            f'  Time            : {appt_time_str}\n'
            f'  Center          : {center_name}\n'
            f'--------------------------------------\n\n'
            f'   Please arrive at the center on time.\n'
            f'   Bring your child\'s vaccination card.\n\n'
            f'Thank you for choosing TIG.\n'
            f'Together we protect every child! \n\n'
            f'Regards,\n'
            f'Trace and Immunize Gujranwala (TIG)'
        )

        try:
            email = EmailMessage(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [patient_email],
            )
            email.send(fail_silently=True)

            # Mark as sent
            appt.reminder_sent = True
            appt.save()

            print(f" Reminder sent to {patient_email}")
            logger.info(f"Reminder sent to {patient_email}")

        except Exception as e:
            print(f"Failed: {e}")
            logger.error(f"Reminder failed: {e}")