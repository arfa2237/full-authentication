from django.shortcuts import render, redirect
from django.contrib import messages

def index(request):
    return render(request, 'publicsite/index.html')

def scheduling(request):
    return render(request, 'publicsite/scheduling.html')

def vpd(request):
    return render(request, 'publicsite/vpd.html')

def faq(request):
    return render(request, 'publicsite/FAQ.html')

def child_vaccination(request):
    return render(request, 'publicsite/Child.html')

def hepatitis(request):
    return render(request, 'publicsite/Hepatitis.html')

def mmr(request):
    return render(request, 'publicsite/MMR.html')

def pneumococcal(request):
    return render(request, 'publicsite/Pneumococcal.html')

def tetanus(request):
    return render(request, 'publicsite/Tetanus.html')

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
