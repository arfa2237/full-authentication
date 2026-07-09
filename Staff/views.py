from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import date, timedelta
from Core.models import Appointment, VaccinationCenter, PatientProfile
from .models import StaffProfile
import dns.resolver


#  Child Vaccine Schedule 
CHILD_VACCINE_SCHEDULE = [
    ('Child Vaccine - At Birth',  None),  # first dose
    ('Child Vaccine - 6 week',    6),     # 6 weeks after birth
    ('Child Vaccine - 10 week',   4),     # 4 weeks after 6-week
    ('Child Vaccine - 14 week',   4),     # 4 weeks after 10-week
    ('Child Vaccine - 9 months',  23),    # 23 weeks after 14-week
    ('Child Vaccine - 15 months', 26),    # 26 weeks after 9-month
]

def get_next_two_doses(current_vaccine, completed_date):
    """Returns next 2 upcoming doses with calculated dates."""
    vaccine_names = [v[0] for v in CHILD_VACCINE_SCHEDULE]
    weeks_list    = [v[1] for v in CHILD_VACCINE_SCHEDULE]

    if current_vaccine not in vaccine_names:
        return []

    current_index = vaccine_names.index(current_vaccine)
    next_doses    = []
    running_date  = completed_date

    for i in range(current_index + 1,
                   min(current_index + 3, len(vaccine_names))):
        weeks        = weeks_list[i] or 0
        running_date = running_date + timedelta(weeks=weeks)
        next_doses.append({
            'vaccine':  vaccine_names[i],
            'date_str': running_date.strftime("%A, %d %B %Y"),
        })

    return next_doses

#  Helper decorator to check if the user is an approved staff member
def staff_required(view_func):
    """Only allow approved staff members."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('staff-login')
        try:
            sp = request.user.staff_profile
            if sp.status != 'approved':
                messages.error(request, 'Your account is pending admin approval.')
                return redirect('staff-login')
        except StaffProfile.DoesNotExist:
            messages.error(request, 'Staff profile not found.')
            return redirect('staff-login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


#  Staff Signup 
def StaffSignup(request):
    centers = VaccinationCenter.objects.filter(is_active=True)

    if request.method == 'POST':
        first_name  = request.POST.get('first_name', '').strip()
        last_name   = request.POST.get('last_name', '').strip()
        username    = request.POST.get('username', '').strip()
        email       = request.POST.get('email', '').strip()
        password    = request.POST.get('password', '').strip()
        phone       = request.POST.get('phone', '').strip()
        designation = request.POST.get('designation', '').strip()
        center_id   = request.POST.get('center', '').strip()

        has_error = False

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            has_error = True

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            has_error = True

        # If email domain is correct check:
        elif not is_email_domain_valid(email):
            messages.error(request, 'Please enter a valid email address with a real domain.')
            has_error = True

        # Block disposable emails
        elif not is_email_allowed(email):
            messages.error(request, 'Disposable or temporary email addresses are not allowed.')
            has_error = True

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            has_error = True

        if has_error:
            return render(request, 'staff/staff_signup.html', {'centers': centers})

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Get center
        center = None
        if center_id:
            try:
                center = VaccinationCenter.objects.get(id=int(center_id))
            except VaccinationCenter.DoesNotExist:
                pass

        # Create staff profile
        StaffProfile.objects.create(
            user=user,
            center=center,
            phone=phone,
            designation=designation,
            status='pending',
        )

        messages.success(request,
            'Registration submitted! Your account is pending admin approval. '
            'You will receive an email once approved.')
        return redirect('staff-login')

    return render(request, 'staff/staff_signup.html', {'centers': centers})


#  Staff Login 
def StaffLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if this user has a staff profile
            try:
                sp = user.staff_profile
                if sp.status == 'approved':
                    login(request, user)
                    return redirect('staff-dashboard')
                elif sp.status == 'pending':
                    messages.error(request,
                        'Your account is pending admin approval. Please wait.')
                else:
                    messages.error(request,
                        'Your account has been rejected. Contact administrator.')
            except StaffProfile.DoesNotExist:
                messages.error(request,
                    'No staff account found. Please register first.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'staff/staff_login.html')


#  Staff Logout 
def StaffLogout(request):
    logout(request)
    return redirect('staff-login')


#  Staff Dashboard 
@staff_required
def StaffDashboard(request):
    sp    = request.user.staff_profile
    today = date.today().strftime("%A, %d %B %Y")

    # Only appointments for staff's assigned center
    base_qs = Appointment.objects.filter(center=sp.center)

    pending_count   = base_qs.filter(status='pending').count()
    scheduled_count = base_qs.filter(status='scheduled').count()
    completed_count = base_qs.filter(status='completed').count()
    missed_count    = base_qs.filter(status='missed').count()
    total_count     = base_qs.count()

    # Latest 5 pending appointments for quick view
    recent_pending = base_qs.filter(status='pending').order_by('appointment_date')[:5]

    return render(request, 'staff/staff_dashboard.html', {
        'sp':               sp,
        'today':            today,
        'pending_count':    pending_count,
        'scheduled_count':  scheduled_count,
        'completed_count':  completed_count,
        'missed_count':     missed_count,
        'total_count':      total_count,
        'recent_pending':   recent_pending,
    })


#  Staff Appointments (full list) 
@staff_required
def StaffAppointments(request):
    sp    = request.user.staff_profile
    today = date.today().strftime("%A, %d %B %Y")

    # Filter by status if requested
    status_filter = request.GET.get('status', 'all')

    base_qs = Appointment.objects.filter(center=sp.center).order_by('appointment_date')

    if status_filter != 'all':
        appointments = base_qs.filter(status=status_filter)
    else:
        appointments = base_qs

    pending_count   = base_qs.filter(status='pending').count()
    scheduled_count = base_qs.filter(status='scheduled').count()
    completed_count = base_qs.filter(status='completed').count()
    missed_count    = base_qs.filter(status='missed').count()
    total_count     = base_qs.count()

    return render(request, 'staff/staff_appointments.html', {
        'sp':               sp,
        'today':            today,
        'appointments':     appointments,
        'status_filter':    status_filter,
        'pending_count':    pending_count,
        'scheduled_count':  scheduled_count,
        'completed_count':  completed_count,
        'missed_count':     missed_count,
        'total_count':      total_count,
    })


#  Update Appointment Status 
@staff_required
def UpdateAppointmentStatus(request, appt_id):
    if request.method == 'POST':
        sp     = request.user.staff_profile
        action = request.POST.get('action', '').strip()

        try:
            appt = Appointment.objects.get(id=appt_id, center=sp.center)
        except Appointment.DoesNotExist:
            messages.error(request, 'Appointment not found.')
            return redirect('staff-appointments')

        # Map action to status
        STATUS_MAP = {
            'confirm':   'scheduled',
            'complete':  'completed',
            'missed':    'missed',
            'cancel':    'cancelled',
        }

        new_status = STATUS_MAP.get(action)
        if not new_status:
            messages.error(request, 'Invalid action.')
            return redirect('staff-appointments')

        old_status = appt.status
        appt.status = new_status
        appt.save()

        #  Send Email Notification to Patient
        patient_email = appt.patient.email
        patient_name  = appt.patient.get_full_name() or appt.patient.username
        vaccine       = appt.vaccine_type
        appt_date     = appt.appointment_date.strftime("%d %B %Y")
        appt_time     = appt.appointment_time.strftime("%I:%M %p")
        center_name   = appt.center.name if appt.center else "the center"

        child_display = appt.child_name if appt.child_name else patient_name

        if action == 'confirm' and patient_email:
            subject = f'TIG — Appointment Confirmed: {vaccine}'
            body = (
                f'Dear {patient_name},\n\n'
                f'Your vaccination appointment has been CONFIRMED.\n\n'
                f'Details:\n'
                f'  Patient (Child) : {child_display}\n'
                f'  Vaccine  : {vaccine} - Dose {appt.dose_number}\n'
                f'  Dose Number     : {appt.dose_number}\n'
                f'  Date     : {appt_date}\n'
                f'  Time     : {appt_time}\n'
                f'  Center   : {center_name}\n'
                f'  Status   : CONFIRMED\n\n'
                f'Please arrive 10 minutes early and bring your vaccine card.\n\n'
                f'Regards,\n'
                f'Trace and Immunize Gujranwala (TIG)'
            )
            _send_email(subject, body, patient_email)

        elif action == 'cancel' and patient_email:
            subject = f'TIG — Appointment Cancelled: {vaccine}'
            body = (
                f'Dear {patient_name},\n\n'
                f'Your vaccination appointment has been <strong>CANCELLED</strong> by healthcare staff.\n\n'
                f'Details:\n'
                f'  Patient (Child) : {child_display}\n'
                f'  Vaccine  : {vaccine} - Dose {appt.dose_number}\n'
                f'  Dose Number     : {appt.dose_number}\n'
                f'  Date     : {appt_date}\n'
                f'  Center   : {center_name}\n'
                f'  Status    : CANCELLED\n\n'
                f'Please log in to book a new appointment.\n\n'
                f'Regards,\n'
                f'Trace and Immunize Gujranwala (TIG)'
            )
            _send_email(subject, body, patient_email)

        elif action == 'complete' and patient_email:

            # .......... Calculate next 2 doses ..........
            next_doses = get_next_two_doses(
                appt.vaccine_type,
                appt.appointment_date
            )

            # .......... Build next dose section ..........
            if next_doses:
                next_dose_lines = (
                    f'\n'
                    f'-------------------------------------------\n'
                    f' NEXT RECOMMENDED DOSES \n'
                    f'-------------------------------------------\n'
                )
                for i, nd in enumerate(next_doses, 1):
                    next_dose_lines += (
                        f'\n  {i}.  {nd["vaccine"]}\n'
                        f'      Recommended Date: {nd["date_str"]}\n'
                    )
                next_dose_lines += (
                    f'\n'
                    f'Please remember to book your next appointment on time\n'
                    f'to ensure your child receives complete immunization.\n'
                )
            else:
                next_dose_lines = (
                    f'\n'
                    f'-------------------------------------------\n'
                    f'\U0001F389  Congratulations!\n'
                    f'-------------------------------------------\n'
                    f'Your child is now fully immunized according\n'
                    f'to the recommended vaccination schedule.\n'
                )

            

            subject = f'TIG — Vaccination Update: {vaccine}'
            body = (
                f'Dear {patient_name},\n\n'
                f'Vaccination Dose Completed\n\n'
                f'-------------------------------------------\n'
                f'COMPLETED APPOINTMENT DETAILS\n'
                f'-------------------------------------------\n\n'
                f'  Patient (Child) : {child_display}\n'
                f'  Vaccine         : {vaccine}\n'
                f'  Dose Number     : {appt.dose_number}\n'
                f'  Date Completed  : {appt_date}\n'
                f'  Time            : {appt_time}\n'
                f'  Center          : {center_name}\n'
                f'  Status          : COMPLETED\n'
                f'{next_dose_lines}\n'
                f'-------------------------------------------\n'
                f'You can download your updated Digital Vaccine\n'
                f'Card by logging in to your TIG account.\n'
                f'-------------------------------------------\n\n'
                f'Thank you for choosing TIG.\n'
                f'\n'
                f'Our mission is to protect every child through complete and timely immunization \n\n'
                f'Regards,\n'
                f'\n'
                f'Trace and Immunize Gujranwala (TIG)'
            )
            _send_email(subject, body, patient_email)

        messages.success(request,
            f'{patient_name}\'s appointment marked as {new_status.upper()} successfully!')

    return redirect('staff-appointments')


#  Staff Patients List 
@staff_required
def StaffPatients(request):
    sp    = request.user.staff_profile
    today = date.today().strftime("%A, %d %B %Y")

    # Get all unique patients who have appointments at this center
    patient_ids = Appointment.objects.filter(
        center=sp.center
    ).values_list('patient_id', flat=True).distinct()

    patients = []
    for pid in patient_ids:
        try:
            user    = User.objects.get(id=pid)
            profile = PatientProfile.objects.get(user=user)
            appts   = Appointment.objects.filter(patient=user, center=sp.center)
            patients.append({
                'user':      user,
                'profile':   profile,
                'total':     appts.count(),
                'completed': appts.filter(status='completed').count(),
                'pending':   appts.filter(status='pending').count(),
            })
        except (User.DoesNotExist, PatientProfile.DoesNotExist):
            pass

    return render(request, 'staff/staff_patients.html', {
        'sp':       sp,
        'today':    today,
        'patients': patients,
    })


#  Email Helper 
def _send_email(subject, body, to_email):
    try:
        email = EmailMessage(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [to_email],
        )
        email.fail_silently = True
        email.send()
    except Exception:
        pass

#.......... Email domain existence check helper .......... 
def is_email_domain_valid(email):
    """Check if the email domain has valid MX records."""
    try:
        domain = email.split('@')[1]
        dns.resolver.resolve(domain, 'MX')
        return True
    except Exception:
        return False
    
BLOCKED_DOMAINS = [
    'mailinator.com', 'guerrillamail.com', 'tempmail.com',
    'throwaway.email', 'fakeinbox.com', 'yopmail.com',
    'sharklasers.com', 'trashmail.com', 'maildrop.cc'
]

def is_email_allowed(email):
    domain = email.split('@')[1].lower()
    return domain not in BLOCKED_DOMAINS