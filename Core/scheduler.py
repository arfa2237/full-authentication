import datetime
import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_appointment_reminders():
    """
    Runs every 5 minutes.
    Sends reminder email 30 minutes before appointment time.
    """
    # Import here to avoid circular import
    from Core.models import Appointment

    now       = timezone.localtime(timezone.now())
    today     = now.date()
    now_time  = now.time()

    # Calculate 30-minute window (25 to 35 minutes from now)
    now_dt       = datetime.datetime.combine(today, now_time)
    window_start = (now_dt + timedelta(minutes=25)).time()
    window_end   = (now_dt + timedelta(minutes=35)).time()

    logger.info(
        f"  Reminder check running at {now_time} "
        f"| Window: {window_start} → {window_end}"
    )

    # Find matching appointments
    upcoming = Appointment.objects.filter(
        appointment_date  = today,
        status__in        = ['scheduled', 'pending'],
        reminder_sent     = False,
        appointment_time__gte = window_start,
        appointment_time__lte = window_end,
    )

    if not upcoming.exists():
        logger.info("No reminders to send right now.")
        return

    for appt in upcoming:
        patient_email = appt.patient.email
        patient_name  = (
            appt.patient.get_full_name() or appt.patient.username
        )
        child_name    = appt.child_name or patient_name
        vaccine       = appt.vaccine_type
        appt_time_str = appt.appointment_time.strftime("%I:%M %p")
        appt_date_str = appt.appointment_date.strftime("%A, %d %B %Y")
        center_name   = (
            appt.center.name if appt.center else "your vaccination center"
        )

        if not patient_email:
            continue

        subject = f'  TIG Reminder - {vaccine} in 30 Minutes!'

        body = (
            f'Dear {patient_name},\n\n'
            f'   APPOINTMENT REMINDER\n\n'
            f'Your child\'s vaccination appointment\n'
            f'is scheduled in 30 MINUTES!\n\n'
            f'-------------------------------------------\n'
            f'APPOINTMENT DETAILS\n'
            f'-------------------------------------------\n'
            f'  Patient (Child) : {child_name}\n'
            f'  Vaccine         : {vaccine}\n'
            f'  Dose Number     : {appt.dose_number}\n'
            f'  Date            : {appt_date_str}\n'
            f'  Time            : {appt_time_str}\n'
            f'  Center          : {center_name}\n'
            f'-------------------------------------------\n\n'
            f'  Please arrive at the center on time.\n'
            f'   Bring your child\'s vaccination card.\n\n'
            f'Thank you for choosing TIG.\n'
            f'Together we protect every child!\n\n'
            f'Regards,\n'
            f'Trace and Immunize Gujranwala (TIG)'
        )

        try:
            email = EmailMessage(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                [patient_email],
            )
            email.fail_silently = True
            email.send()

            # Mark as sent: prevents duplicate emails
            appt.reminder_sent = True
            appt.save()

            logger.info(
                f" Reminder sent → {patient_email} "
                f"for {vaccine} at {appt_time_str}"
            )

        except Exception as e:
            logger.error(f" Failed to send reminder: {e}")