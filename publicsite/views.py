from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.cache import add_never_cache_headers 

def index(request):
    response = render(request, 'publicsite/index.html')
    add_never_cache_headers(response)  # always refresh 
    return response

def scheduling(request):
    response = render(request, 'publicsite/scheduling.html')
    add_never_cache_headers(response)
    return response

@login_required(login_url='/patient/login/') 
def appointment(request):
    return render(request, 'publicsite/appointment.html') 

def tracking(request):
    return render(request, 'publicsite/tracking.html') 

def vpd(request):
    response = render(request, 'publicsite/vpd.html')
    add_never_cache_headers(response)
    return response

def child_vaccination(request):
    return render(request, 'publicsite/Child.html')

def hepatitis(request):
    return render(request, 'publicsite/Hepatitis.html')

def mmr(request):
    return render(request, 'publicsite/MMR.html')

def measles(request):
    return render(request, 'publicsite/measles.html')

def mumps(request):
    return render(request, 'publicsite/mumps.html')

def rubella(request):
    return render(request, 'publicsite/rubella.html') 

def pneumococcal(request):
    return render(request, 'publicsite/Pneumococcal.html')

def tetanus(request):
    return render(request, 'publicsite/Tetanus.html')

def vpd(request):
    return render(request, 'publicsite/vpd.html')

def faq(request):
    response = render(request, 'publicsite/FAQ.html')
    add_never_cache_headers(response)
    return response

def nearby(request):
    response = render(request, 'publicsite/nearby.html')
    add_never_cache_headers(response)
    return response

def patient(request):
    if request.method == 'POST':
        messages.success(request, 'Patient data saved successfully!')
        return redirect('patient')
    return render(request, 'publicsite/patient.html')

def blog1(request):
    return render(request, 'publicsite/blog1.html')

def blog2(request):
    return render(request, 'publicsite/blog2.html')

def blog3(request):
    return render(request, 'publicsite/blog3.html')
def nearby(request):
    return render(request, 'publicsite/nearby.html')

def chatbot(request):
    return render(request, "chatbot.html")
