from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from urllib import request
from datetime import date
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from django.views import View
from django.utils.cache import add_never_cache_headers
from datetime import date, datetime
from .models import PatientProfile, VaccinationCenter, Appointment
from .models import *


# Create your views here.
@login_required
def Home(request):
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    today = date.today().strftime("%A, %d %B %Y")
    # All appointments
    all_appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('-appointment_date')[:4]  # latest 4 for dashboard

    # Stat counts
    pending_count   = Appointment.objects.filter(patient=request.user, status='pending').count()
    completed_count = Appointment.objects.filter(patient=request.user, status='completed').count()
    upcoming_count  = Appointment.objects.filter(patient=request.user, status__in=['pending','scheduled']).count()
    missed_count    = Appointment.objects.filter(patient=request.user, status='missed').count()

    # Immunization percentage (out of 13 total doses)
    TOTAL_DOSES = 13
    percent = int((completed_count / TOTAL_DOSES) * 100) if completed_count else 0

    # Vaccine progress for progress bars
    VACCINE_TOTAL_DOSES = {
        'Child Vaccine - At Birth':     1,
        'Child Vaccine - 6 week':       2,
        'Child Vaccine - 10 week':      3,
        'Child Vaccine - 14 week':      4,
        'Child Vaccine - 9 months':     5,
        'Child Vaccine - 15 months':    6,
    }
    COLORS = ['green', 'purple', 'orange', 'purple', 'green', 'blue']

    vaccine_progress = []
    for i, (vac_name, total) in enumerate(VACCINE_TOTAL_DOSES.items()):
        done = Appointment.objects.filter(
            patient=request.user,
            vaccine_type=vac_name,
            status='completed'
        ).count()
        vac_percent = int((done / total) * 100) if total > 0 else 0
        vaccine_progress.append({
            'name':    vac_name,
            'done':    done,
            'total':   total,
            'percent': vac_percent,
            'color':   COLORS[i % len(COLORS)],
        })

    return render(request, 'dashboard.html', {
        'profile':          profile,
        'today':            today,
        'appointments':     all_appointments,
        'pending_count':    pending_count,
        'completed_count':  completed_count,
        'upcoming_count':   upcoming_count,
        'missed_count':     missed_count,
        'immunization_pct': percent,
        'vaccine_progress': vaccine_progress,
        'completed_doses':  completed_count,
    })
def RegisterView(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_data_has_error = False

        # make sure email and username are not being used
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, 'Username is already taken')

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, 'Email is already taken')
        # Check password length
        if password and len(password) < 8:
            user_data_has_error = True
            messages.error(request, 'Password must be at least 8 characters')
        # create a new user if there is no error
        if user_data_has_error:
            return redirect('register')
        else:
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )

            PatientProfile.objects.create(user=new_user) 
            messages.success(request, 'Account created Successfully!')
            return redirect('login')

    return render(request, 'register.html')

def LogoutView(request):

    logout(request)
    response = redirect('login') 
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def ForgotPassword(request):

    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            
            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
        
            email_message = EmailMessage(
                'Reset your password', # email subject
                email_body,
                settings.EMAIL_HOST_USER, # email sender
                [email] # email  receiver 
            )

            email_message.fail_silently = True
            email_message.send()

            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')
            
    
    return render(request, 'forgot_password.html')

def PasswordResetSent(request, reset_id):

    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')


def ResetPassword(request, reset_id):
    import re

    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == 'POST':
            password = request.POST.get('password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()

            passwords_have_error = False

            # Check if passwords are empty
            if not password or not confirm_password:
                passwords_have_error = True
                messages.error(request, 'Password fields cannot be empty')

            if password and confirm_password and password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            # Server-side password validation (matching client-side rules)
            if password and not passwords_have_error:
                # Minimum length
                if len(password) < 8:
                    passwords_have_error = True
                    messages.error(request, 'Password must be at least 8 characters long')
                
                # Maximum length
                elif len(password) > 128:
                    passwords_have_error = True
                    messages.error(request, 'Password cannot exceed 128 characters')
                
                # At least one uppercase letter
                elif not re.search(r'[A-Z]', password):
                    passwords_have_error = True
                    messages.error(request, 'Password must contain at least one uppercase letter (A-Z)')
                
                # At least one lowercase letter
                elif not re.search(r'[a-z]', password):
                    passwords_have_error = True
                    messages.error(request, 'Password must contain at least one lowercase letter (a-z)')
                
                # At least one number
                elif not re.search(r'\d', password):
                    passwords_have_error = True
                    messages.error(request, 'Password must contain at least one number (0-9)')
                
                # At least one special character
                elif not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?~`]', password):
                    passwords_have_error = True
                    messages.error(request, 'Password must contain at least one special character (!@#$%^&* etc)')
                
                # No spaces allowed
                elif ' ' in password:
                    passwords_have_error = True
                    messages.error(request, 'Password cannot contain spaces')
                
                # Not a common password
                elif password.lower() in ['password', '12345678', 'qwerty123', 'admin123', 'welcome123', 'password123', 'abc123456']:
                    passwords_have_error = True
                    messages.error(request, 'Password is too common. Please choose a stronger password')
                
                # No 4+ repeated characters
                elif re.search(r'(.)\1{3,}', password):
                    passwords_have_error = True
                    messages.error(request, 'Password cannot have 4 or more repeated characters in a row')
                
                # No sequential characters
                elif re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|012|123|234|345|456|567|678|789)', password.lower()):
                    passwords_have_error = True
                    messages.error(request, 'Password cannot contain sequential characters (like "123" or "abc")')

            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')
                password_reset_id.delete()

            if not passwords_have_error:
                user = User.objects.get(pk=password_reset_id.user.pk)
                user.set_password(password)
                user.save()

                # Verify the password was set correctly
                if user.check_password(password):
                    password_reset_id.delete()
                    messages.success(request, 'Password reset successfully!')
                    return redirect('login')
                else:
                    messages.error(request, 'Error resetting password. Please try again.')
                    return redirect('reset-password', reset_id=reset_id)
            else:
                # redirect back to password reset page and display errors
                return redirect('reset-password', reset_id=reset_id)

            
    except PasswordReset.DoesNotExist:
        
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'reset_password.html')




@login_required
def BookAppointment(request):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    today       = date.today().strftime("%A, %d %B %Y")
    centers     = VaccinationCenter.objects.filter(is_active=True)

    # Static vaccine list (jb tk static rehy gy Vaccine mode ni bnaty)
    vaccines = [
        {'name': 'Child Vaccine - At Birth',        'doses': 1,  'icon': 'fa-solid fa-shield-halved'},
        {'name': 'Child Vaccine - 6 week',          'doses': 2,  'icon': 'fa-solid fa-virus-slash'},
        {'name': 'Child Vaccine - 10 week',         'doses': 3,  'icon': 'fa-solid fa-syringe'},
        {'name': 'Child Vaccine - 14 week',         'doses': 4,  'icon': 'fa-solid fa-lungs'},
        {'name': 'Child Vaccine - 9 months',        'doses': 5,  'icon': 'fa-solid fa-baby'},
        {'name': 'Child Vaccine - 15 months',       'doses': 6,  'icon': 'fa-solid fa-biohazard'},
    ]

    if request.method == 'POST':
        vaccine_type = request.POST.get('vaccine_type', '').strip()
        dose_number  = request.POST.get('dose_number',  '1').strip()
        center_id    = request.POST.get('center_id',    '').strip()
        appt_date    = request.POST.get('appt_date',    '').strip()
        appt_time    = request.POST.get('appt_time',    '').strip()
        notes        = request.POST.get('notes',        '').strip()
        # NEW fields
        child_name     = request.POST.get('child_name',     '').strip()
        child_gender   = request.POST.get('child_gender',   '').strip()
        guardian_name  = request.POST.get('guardian_name',  '').strip()
        guardian_cnic  = request.POST.get('guardian_cnic',  '').strip()

        # .......................... Validation ..........................................
        has_error = False

        if not vaccine_type:
            messages.error(request, 'Please select a vaccine type.')
            has_error = True
        if not child_name:
            messages.error(request, 'Please enter the child\'s name.')
            has_error = True

        if not child_gender:
            messages.error(request, 'Please select the child\'s gender.')
            has_error = True

        if not guardian_cnic:
            messages.error(request, 'Please enter guardian CNIC.')
            has_error = True
        
        elif len(guardian_cnic.replace('-', '')) != 13:
            messages.error(request, 'CNIC must be 13 digits.')
            has_error = True

        if not guardian_name:
            messages.error(request, 'Please enter guardian name.')
            has_error = True

        if not appt_date:
            messages.error(request, 'Please select an appointment date.')
            has_error = True
        else:
            try:
                parsed_date = datetime.strptime(appt_date, '%Y-%m-%d').date()
                if parsed_date < date.today():
                    messages.error(request, 'Appointment date cannot be in the past.')
                    has_error = True
            except ValueError:
                messages.error(request, 'Invalid date format.')
                has_error = True

        if not appt_time:
            messages.error(request, 'Please select a time slot.')
            has_error = True
        else:
            try:
                parsed_time = datetime.strptime(appt_time, '%H:%M').time()
            except ValueError:
                messages.error(request, 'Invalid time format.')
                has_error = True

        # Duplicate check: same vaccine + dose already scheduled
        if not has_error:
            duplicate = Appointment.objects.filter(
                patient=request.user,
                vaccine_type=vaccine_type,
                dose_number=int(dose_number),
                status='scheduled'
            ).exists()

            if duplicate:
                messages.error(
                    request,
                    f'You already have a scheduled appointment for {vaccine_type} Dose {dose_number}.'
                )
                has_error = True

        if has_error:
            return render(request, 'book_appointment.html', {
                'profile':  profile,
                'today':    today,
                'centers':  centers,
                'vaccines': vaccines,
                'pending_count': Appointment.objects.filter(patient=request.user, status='pending').count(),  # ADD THIS
            })

        # .......................... Save Appointment ............................
        center = None
        if center_id:
            try:
                center = VaccinationCenter.objects.get(id=int(center_id))
            except (VaccinationCenter.DoesNotExist, ValueError):
                pass

        Appointment.objects.create(
            patient          = request.user,
            center           = center,
            vaccine_type     = vaccine_type,
            dose_number      = int(dose_number) if dose_number.isdigit() else 1,
            appointment_date = parsed_date,
            appointment_time = parsed_time,
            notes            = notes,
            status           = 'pending', #default status when booking an appointment
            child_name       = child_name,
            child_gender     = child_gender,
            guardian_name    = guardian_name,
            guardian_cnic    = guardian_cnic,
        )
        messages.success(
            request,
            f'Appointment request submitted! Vaccine {vaccine_type} Dose {dose_number} on {parsed_date.strftime("%d %B %Y")} — Status: Pending Confirmation.'
        )
          # url bd mn bnaye gy 
        return redirect('my-appointments')
    return render(request, 'book_appointment.html', {
        'profile':  profile,
        'today':    today,
        'centers':  centers,
        'vaccines': vaccines,
    })



@login_required
def MyAppointments(request):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    today       = date.today().strftime("%A, %d %B %Y")

    appointments = Appointment.objects.filter(patient=request.user).order_by('-appointment_date')

    # Counts for stats and filter badges
    total_count     = appointments.count()
    pending_count   = appointments.filter(status='pending').count()
    scheduled_count = appointments.filter(status='scheduled').count()
    completed_count = appointments.filter(status='completed').count()
    missed_count    = appointments.filter(status='missed').count()
    cancelled_count = appointments.filter(status='cancelled').count()

    return render(request, 'my_appointments.html', {
        'profile':         profile,
        'today':           today,
        'appointments':    appointments,
        'total_count':     total_count,
        'pending_count':   pending_count,
        'scheduled_count': scheduled_count,
        'completed_count': completed_count,
        'missed_count':    missed_count,
        'cancelled_count': cancelled_count,
    })


@login_required
def CancelAppointment(request, appt_id):
    if request.method == 'POST':
        try:
            appt = Appointment.objects.get(id=appt_id, patient=request.user)
            # Only allow cancel if still pending or scheduled
            if appt.status in ['pending', 'scheduled']:
                appt.status = 'cancelled'
                appt.save()
                messages.success(request, f'{appt.vaccine_type} appointment cancelled successfully.')
            else:
                messages.error(request, 'This appointment cannot be cancelled.')
        except Appointment.DoesNotExist:
            messages.error(request, 'Appointment not found.')
    return redirect('my-appointments')




@login_required
def VaccineCard(request):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    today       = date.today().strftime("%A, %d %B %Y")

    # All appointments for this user
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('vaccine_type', 'dose_number')

    # Count completed doses
    completed_doses = appointments.filter(status='completed').count()

    pending_count = appointments.filter(status='pending').count()

    #  Get child info from latest appointment 
    latest = appointments.first()
    child_name    = latest.child_name    if latest else None
    child_gender  = latest.child_gender  if latest else None
    guardian_name = latest.guardian_name if latest else None
    guardian_cnic = latest.guardian_cnic if latest else None

    # Vaccine progress calculation
    VACCINE_TOTAL_DOSES = {
        'Child Vaccine - At Birth':     1,
        'Child Vaccine - 6 week':       2,
        'Child Vaccine - 10 week':      3,
        'Child Vaccine - 14 week':      4,
        'Child Vaccine - 9 months':     5,
        'Child Vaccine - 15 months':    6,
    }

    COLORS = ['purple', 'green', 'orange', 'blue', 'purple', 'green']

    vaccine_progress = []
    for i, (vac_name, total) in enumerate(VACCINE_TOTAL_DOSES.items()):
        done = appointments.filter(
            vaccine_type=vac_name,
            status='completed'
        ).count()
        percent = int((done / total) * 100) if total > 0 else 0
        vaccine_progress.append({
            'name':    vac_name,
            'done':    done,
            'total':   total,
            'percent': percent,
            'color':   COLORS[i % len(COLORS)],
        })

    return render(request, 'vaccine_card.html', {
        'profile':          profile,
        'today':            today,
        'appointments':     appointments,
        'completed_doses':  completed_doses,
        'pending_count':    pending_count,
        'vaccine_progress': vaccine_progress,
        'child_name':       child_name,
        'child_gender':     child_gender,
        'guardian_name':    guardian_name,
        'guardian_cnic':    guardian_cnic,
    })


@login_required
def DownloadVaccineCard(request):
    """Generate and download vaccine card as PDF using ReportLab"""

    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('vaccine_type', 'dose_number')

    # .......................... Setup PDF .........................................
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="TIG_VaccineCard_{profile.unique_pin}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4  # 595 x 842 points

    # .............................. Colors ........................................
    navy      = colors.HexColor('#28375f')
    accent    = colors.HexColor('#6884d3')
    light_bg  = colors.HexColor('#f3f0ff')
    success   = colors.HexColor('#43a047')
    warning   = colors.HexColor('#fb8c00')
    danger    = colors.HexColor('#f06272')
    muted     = colors.HexColor('#6b7db3')
    white     = colors.white

    #  ......................... HEADER BANNER ......................................
    p.setFillColor(navy)
    p.rect(0, height - 120, width, 120, fill=1, stroke=0)

    # Header text
    p.setFillColor(white)
    p.setFont('Helvetica-Bold', 22)
    p.drawString(40, height - 50, 'DIGITAL VACCINATION CARD')

    p.setFont('Helvetica', 11)
    p.setFillColor(colors.HexColor('#c9d6ff'))
    p.drawString(40, height - 70, 'Trace and Immunize Gujranwala (TIG)')

    # Issued date on right
    p.setFont('Helvetica', 9)
    p.setFillColor(colors.HexColor('#c9d6ff'))
    issued_text = f'Issued: {date.today().strftime("%d %B %Y")}'
    p.drawRightString(width - 40, height - 50, issued_text)

    # .............................. PATIENT INFO SECTION ................................
    y = height - 160

    latest_appt   = appointments.first()
    child_name    = latest_appt.child_name    if latest_appt and latest_appt.child_name    else ''
    child_gender  = latest_appt.child_gender  if latest_appt and latest_appt.child_gender  else ''
    guardian_name = latest_appt.guardian_name if latest_appt and latest_appt.guardian_name else ''
    guardian_cnic = latest_appt.guardian_cnic if latest_appt and latest_appt.guardian_cnic else ''

    # Patient info box
    p.setFillColor(light_bg)
    p.roundRect(30, y - 110, width - 60, 120, 10, fill=1, stroke=0)

    # Child Name (big title)
    p.setFillColor(navy)
    p.setFont('Helvetica-Bold', 14)
    display_name = child_name if child_name else f'{request.user.first_name} {request.user.last_name}'.strip()
    p.drawString(50, y - 22, f'Patient: {display_name}')

    # Gender
    p.setFont('Helvetica', 10)
    p.setFillColor(muted)
    if child_gender:
        gender_text = 'Boy (Male)' if child_gender == 'male' else 'Girl (Female)'
        p.drawString(50, y - 40, f'Gender: {gender_text}')

    # Guardian Name
    if guardian_name:
        p.drawString(50, y - 58, f'Guardian: {guardian_name}')

    # Guardian CNIC
    if guardian_cnic:
        p.drawString(50, y - 74, f'CNIC: {guardian_cnic}')

    # PIN
    p.drawString(50, y - 92, f'PIN: {profile.unique_pin}')

    # ── Completed doses badge (right side) ────────────────────────────────
    completed_doses = appointments.filter(status='completed').count()
    p.setFillColor(accent)
    p.roundRect(width - 160, y - 100, 120, 78, 8, fill=1, stroke=0)
    p.setFillColor(white)
    p.setFont('Helvetica-Bold', 28)
    p.drawCentredString(width - 100, y - 55, str(completed_doses))
    p.setFont('Helvetica', 8)
    p.drawCentredString(width - 100, y - 75, 'Doses Completed')
    # ........................ VACCINATION RECORDS TABLE ..............................
    y = y - 130

    # Table title
    p.setFillColor(navy)
    p.setFont('Helvetica-Bold', 12)
    p.drawString(30, y, 'VACCINATION RECORDS')

    y -= 8
    # Divider line
    p.setStrokeColor(accent)
    p.setLineWidth(2)
    p.line(30, y, width - 30, y)
    y -= 20

    # Table header
    col_widths = [180, 60, 160, 100]
    col_x = [30, 210, 270, 430]
    headers = ['VACCINE', 'DOSE', 'CENTER', 'STATUS']

    p.setFillColor(accent)
    p.rect(30, y - 8, width - 60, 22, fill=1, stroke=0)

    p.setFillColor(white)
    p.setFont('Helvetica-Bold', 9)
    for i, header in enumerate(headers):
        p.drawString(col_x[i] + 6, y + 5, header)

    y -= 22

    # Table rows
    STATUS_COLORS = {
        'completed': success,
        'pending':   warning,
        'scheduled': accent,
        'missed':    danger,
        'cancelled': muted,
    }

    row_count = 0
    if appointments.exists():
        for appt in appointments:
            # Alternating row background
            if row_count % 2 == 0:
                p.setFillColor(colors.HexColor('#f8f9ff'))
                p.rect(30, y - 8, width - 60, 22, fill=1, stroke=0)

            p.setFillColor(navy)
            p.setFont('Helvetica', 9)

            # Vaccine name
            p.drawString(col_x[0] + 6, y + 5, appt.vaccine_type[:25])

            # Dose number
            dose_label = 'B' if appt.dose_number == 0 else str(appt.dose_number)
            p.drawString(col_x[1] + 6, y + 5, f'Dose {dose_label}')

            # Center
            center_name = appt.center.name[:22] if appt.center else 'Not assigned'
            p.drawString(col_x[2] + 6, y + 5, center_name)

            # Status with color
            status_color = STATUS_COLORS.get(appt.status, muted)
            p.setFillColor(status_color)
            p.roundRect(col_x[3] + 4, y - 4, 80, 16, 4, fill=1, stroke=0)
            p.setFillColor(white)
            p.setFont('Helvetica-Bold', 8)
            p.drawCentredString(col_x[3] + 44, y + 4, appt.status.upper())

            # Row divider
            p.setStrokeColor(colors.HexColor('#e8ecff'))
            p.setLineWidth(0.5)
            p.line(30, y - 8, width - 30, y - 8)

            y -= 22
            row_count += 1

            # New page if needed
            if y < 100:
                p.showPage()
                y = height - 60
    else:
        p.setFillColor(muted)
        p.setFont('Helvetica', 10)
        p.drawCentredString(width / 2, y, 'No vaccination records found.')
        y -= 22

    # ................................ FOOTER ........................................
    y_footer = 60
    p.setStrokeColor(accent)
    p.setLineWidth(1)
    p.line(30, y_footer + 20, width - 30, y_footer + 20)

    p.setFillColor(muted)
    p.setFont('Helvetica', 8)
    p.drawCentredString(width / 2, y_footer + 8,
        'This is an official digital vaccination record issued by Trace and Immunize Gujranwala (TIG)')
    p.drawCentredString(width / 2, y_footer - 4,
        f'Generated on {date.today().strftime("%d %B %Y")} | PIN: {profile.unique_pin}')

    p.save()
    return response

    # ADD THIS FUNCTION at the bottom of your Core/views.py ......................

@login_required
def MyRecords(request):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    today       = date.today().strftime("%A, %d %B %Y")

    # All appointments
    appointments = Appointment.objects.filter(patient=request.user)

    # Stat counts ................................................
    total_count     = appointments.count()
    pending_count   = appointments.filter(status='pending').count()
    scheduled_count = appointments.filter(status='scheduled').count()
    completed_count = appointments.filter(status='completed').count()
    missed_count    = appointments.filter(status='missed').count()
    cancelled_count = appointments.filter(status='cancelled').count()

    # Vaccine progress ............................................................
    VACCINE_TOTAL_DOSES = {
        'Child Vaccine - At Birth':     1,
        'Child Vaccine - 6 week':       2,
        'Child Vaccine - 10 week':      3,
        'Child Vaccine - 14 week':      4,
        'Child Vaccine - 9 months':     5,
        'Child Vaccine - 15 months':    6,
    }
    TOTAL_DOSES = sum(VACCINE_TOTAL_DOSES.values())  # 13

    CHART_COLORS = ['#6884d3', '#43a047', '#fb8c00', '#f06272', '#1a6fb3', '#28375f']

    vaccine_progress = []
    for i, (vac_name, total) in enumerate(VACCINE_TOTAL_DOSES.items()):
        done = appointments.filter(
            vaccine_type=vac_name,
            status='completed'
        ).count()
        percent = int((done / total) * 100) if total > 0 else 0
        vaccine_progress.append({
            'name':    vac_name,
            'done':    done,
            'total':   total,
            'percent': percent,
            'color':   CHART_COLORS[i % len(CHART_COLORS)],
        })

    # Immunization percentage  .........................
    immunization_pct = int((completed_count / TOTAL_DOSES) * 100) if completed_count else 0

    # Data for Donut chart (appointment status) ..............................
    donut_data = {
        'labels': ['Completed', 'Pending', 'Scheduled', 'Missed', 'Cancelled'],
        'data':   [completed_count, pending_count, scheduled_count, missed_count, cancelled_count],
        'colors': ['#43a047', '#fb8c00', '#6884d3', '#f06272', '#9e9e9e'],
    }

    # Data for horizontal bar chart (vaccine progress) .....................
    bar_labels  = [v['name'] for v in vaccine_progress]
    bar_done    = [v['done'] for v in vaccine_progress]
    bar_total   = [v['total'] for v in vaccine_progress]
    bar_colors  = [v['color'] for v in vaccine_progress]

    # Recent completed appointments .....................................
    recent_completed = appointments.filter(
        status='completed'
    ).order_by('-appointment_date')[:5]

    return render(request, 'my_records.html', {
        'profile':           profile,
        'today':             today,
        'total_count':       total_count,
        'pending_count':     pending_count,
        'scheduled_count':   scheduled_count,
        'completed_count':   completed_count,
        'missed_count':      missed_count,
        'cancelled_count':   cancelled_count,
        'immunization_pct':  immunization_pct,
        'vaccine_progress':  vaccine_progress,
        'recent_completed':  recent_completed,
        # JSON-safe data for charts
        'donut_labels':      donut_data['labels'],
        'donut_data':        donut_data['data'],
        'donut_colors':      donut_data['colors'],
        'bar_labels':        bar_labels,
        'bar_done':          bar_done,
        'bar_total':         bar_total,
        'bar_colors':        bar_colors,
        'TOTAL_DOSES':       TOTAL_DOSES,
    })
        
class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')         
        next_url = request.GET.get('next', '')
        response = render(request, 'login.html', {'next': next_url}) 
        add_never_cache_headers(response)  
        return response

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # If next_url exists go there, else go to index (home)
            return redirect(next_url) if next_url else redirect('index')
        else:
            messages.error(request, 'Invalid credentials')
            response = render(request, 'login.html', {'next': next_url})
            add_never_cache_headers(response) 
            return response
