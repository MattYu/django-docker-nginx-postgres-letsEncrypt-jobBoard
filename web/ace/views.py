from django.http import HttpResponse
from django.shortcuts import render

from companies.models import Company
from jobapplications.models import JobApplication
from joblistings.models import Job
from accounts.models import Candidate

def home_page(request):
    context = {}
    
    context["jobCount"] = Job.objects.count()

    context["companyCount"] = Company.objects.count()

    context["applicationCount"] = JobApplication.objects.count()

    context["candidateCount"] = Candidate.objects.count()

    if 'warning' in request.session:
        context['warning'] = request.session['warning']
        del request.session['warning']
    if 'success' in request.session:
        context['success'] = request.session['success']
        del request.session['success']
    if 'info' in request.session:
        context['info'] = request.session['info']
        del request.session['info']
    if 'danger' in request.session:
        context['danger'] = request.session['danger']
        del request.session['danger']

    return render(request, "home-4.html", context)