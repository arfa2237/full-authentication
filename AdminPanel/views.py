from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Count
from datetime import date
from Core.models import Appointment, VaccinationCenter, PatientProfile
from Staff.models import StaffProfile
from .models import AdminProfile
from django.db.models.functions import TruncMonth


#  Helper decorator 
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin-login')
        try:
            request.user.admin_profile
        except AdminProfile.DoesNotExist:
            messages.error(request, 'You do not have admin access.')
            return redirect('admin-login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


#  Admin Login 
def AdminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                user.admin_profile
                login(request, user)
                return redirect('admin-dashboard')
            except AdminProfile.DoesNotExist:
                messages.error(request, 'You do not have admin access.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'adminpanel/admin_login.html')


#  Admin Logout 
def AdminLogout(request):
    logout(request)
    return redirect('admin-login')


#  Admin Dashboard 
@admin_required
def AdminDashboard(request):
    today = date.today().strftime("%A, %d %B %Y")

    # Stats
    total_patients    = PatientProfile.objects.count()
    total_staff       = StaffProfile.objects.filter(status='approved').count()
    pending_staff     = StaffProfile.objects.filter(status='pending').count()
    total_appts       = Appointment.objects.count()
    pending_appts     = Appointment.objects.filter(status='pending').count()
    completed_appts   = Appointment.objects.filter(status='completed').count()
    total_centers     = VaccinationCenter.objects.filter(is_active=True).count()

    # Recent pending staff
    pending_staff_list = StaffProfile.objects.filter(
        status='pending'
    ).order_by('-created_at')[:5]

    # Recent appointments
    recent_appts = Appointment.objects.order_by('-created_at')[:5]

    return render(request, 'adminpanel/admin_dashboard.html', {
        'today':            today,
        'total_patients':   total_patients,
        'total_staff':      total_staff,
        'pending_staff':    pending_staff,
        'total_appts':      total_appts,
        'pending_appts':    pending_appts,
        'completed_appts':  completed_appts,
        'total_centers':    total_centers,
        'pending_staff_list': pending_staff_list,
        'recent_appts':     recent_appts,
    })


#  Manage Staff 
@admin_required
def AdminStaff(request):
    today = date.today().strftime("%A, %d %B %Y")
    status_filter = request.GET.get('status', 'all')

    if status_filter != 'all':
        staff_list = StaffProfile.objects.filter(status=status_filter).order_by('-created_at')
    else:
        staff_list = StaffProfile.objects.all().order_by('-created_at')

    pending_count  = StaffProfile.objects.filter(status='pending').count()
    approved_count = StaffProfile.objects.filter(status='approved').count()
    rejected_count = StaffProfile.objects.filter(status='rejected').count()

    return render(request, 'adminpanel/admin_staff.html', {
        'today':          today,
        'staff_list':     staff_list,
        'status_filter':  status_filter,
        'pending_count':  pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    })


#  Update Staff Status 
@admin_required
def UpdateStaffStatus(request, staff_id):
    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        sp     = get_object_or_404(StaffProfile, id=staff_id)

        if action == 'approve':
            sp.status = 'approved'
            sp.save()
            # Send approval email
            _send_email(
                f'TIG - Staff Account Approved',
                f'Dear {sp.user.get_full_name()},\n\n'
                f'Your healthcare staff account has been APPROVED!\n\n'
                f'You can now login at: https://tig-gujranwala.com/staff/login/\n'
                f'Username: {sp.user.username}\n\n'
                f'Regards,\nTIG Admin',
                sp.user.email
            )
            messages.success(request, f'{sp.user.get_full_name()} approved successfully! Email sent.')

        elif action == 'reject':
            sp.status = 'rejected'
            sp.save()
            # Send rejection email
            _send_email(
                f'TIG — Staff Account Update',
                f'Dear {sp.user.get_full_name()},\n\n'
                f'Unfortunately your staff account registration has been rejected.\n\n'
                f'Please contact the administrator for more information.\n\n'
                f'Regards,\nTIG Admin',
                sp.user.email
            )
            messages.error(request, f'{sp.user.get_full_name()} rejected.')

    return redirect('admin-staff')


#  Manage Users/Patients 
@admin_required
def AdminUsers(request):
    today    = date.today().strftime("%A, %d %B %Y")
    profiles = PatientProfile.objects.all().order_by('-id')

    users_data = []
    for profile in profiles:
        appts = Appointment.objects.filter(patient=profile.user)
        users_data.append({
            'profile':   profile,
            'total':     appts.count(),
            'completed': appts.filter(status='completed').count(),
            'pending':   appts.filter(status='pending').count(),
        })

    return render(request, 'adminpanel/admin_users.html', {
        'today':      today,
        'users_data': users_data,
    })


#  Manage Centers
@admin_required
def AdminCenters(request):
    today   = date.today().strftime("%A, %d %B %Y")
    centers = VaccinationCenter.objects.all().order_by('name')

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'add':
            name         = request.POST.get('name', '').strip()
            address      = request.POST.get('address', '').strip()
            availability = request.POST.get('availability', '').strip()
            latitude     = request.POST.get('latitude', '') or None
            longitude    = request.POST.get('longitude', '') or None

            if name and address:
                VaccinationCenter.objects.create(
                    name=name,
                    address=address,
                    availability=availability,
                    latitude=latitude,
                    longitude=longitude,
                    is_active=True,
                )
                messages.success(request, f'{name} added successfully!')
            else:
                messages.error(request, 'Name and address are required.')

        elif action == 'toggle':
            center_id = request.POST.get('center_id')
            center    = get_object_or_404(VaccinationCenter, id=center_id)
            center.is_active = not center.is_active
            center.save()
            status = 'activated' if center.is_active else 'deactivated'
            messages.success(request, f'{center.name} {status}!')

        elif action == 'delete':
            center_id = request.POST.get('center_id')
            center    = get_object_or_404(VaccinationCenter, id=center_id)
            name      = center.name
            center.delete()
            messages.success(request, f'{name} deleted!')

        return redirect('admin-centers')

    return render(request, 'adminpanel/admin_centers.html', {
        'today':   today,
        'centers': centers,
    })


#  View All Appointments 
@admin_required
def AdminAppointments(request):
    today         = date.today().strftime("%A, %d %B %Y")
    status_filter = request.GET.get('status', 'all')

    if status_filter != 'all':
        appointments = Appointment.objects.filter(status=status_filter).order_by('-created_at')
    else:
        appointments = Appointment.objects.all().order_by('-created_at')

    total_count     = Appointment.objects.count()
    pending_count   = Appointment.objects.filter(status='pending').count()
    scheduled_count = Appointment.objects.filter(status='scheduled').count()
    completed_count = Appointment.objects.filter(status='completed').count()
    missed_count    = Appointment.objects.filter(status='missed').count()

    return render(request, 'adminpanel/admin_appointments.html', {
        'today':          today,
        'appointments':   appointments,
        'status_filter':  status_filter,
        'total_count':    total_count,
        'pending_count':  pending_count,
        'scheduled_count': scheduled_count,
        'completed_count': completed_count,
        'missed_count':   missed_count,
    })


#  Email Helper 
def _send_email(subject, body, to_email):
    try:
        email = EmailMessage(
            subject, body,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
        )
        email.fail_silently = True
        email.send()
    except Exception:
        pass

@admin_required
def AdminStatistics(request):
    today = date.today().strftime("%A, %d %B %Y")

    #  System wide counts 
    total_patients    = PatientProfile.objects.count()
    total_staff       = StaffProfile.objects.filter(status='approved').count()
    total_centers     = VaccinationCenter.objects.filter(is_active=True).count()
    total_appts       = Appointment.objects.count()
    completed_appts   = Appointment.objects.filter(status='completed').count()
    pending_appts     = Appointment.objects.filter(status='pending').count()
    missed_appts      = Appointment.objects.filter(status='missed').count()
    cancelled_appts   = Appointment.objects.filter(status='cancelled').count()
    scheduled_appts   = Appointment.objects.filter(status='scheduled').count()


    #  Donut data
    donut_data   = [completed_appts, pending_appts, scheduled_appts, missed_appts, cancelled_appts]
    donut_labels = ['Completed', 'Pending', 'Scheduled', 'Missed', 'Cancelled']
    donut_colors = ['#43a047', '#fb8c00', '#6884d3', '#f06272', '#9e9e9e']

    return render(request, 'adminpanel/admin_statistics.html', {
        'today':            today,
        'total_patients':   total_patients,
        'total_staff':      total_staff,
        'total_centers':    total_centers,
        'total_appts':      total_appts,
        'completed_appts':  completed_appts,
        'pending_appts':    pending_appts,
        'missed_appts':     missed_appts,
        'cancelled_appts':  cancelled_appts,
        'scheduled_appts':  scheduled_appts,
        # JSON data for charts
        'donut_labels':     donut_labels,
        'donut_data':       donut_data,
        'donut_colors':     donut_colors,
    })