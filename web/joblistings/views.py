#from django.views import ListView
from django.shortcuts import render, get_object_or_404
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q

from ace.settings import GOOGLE_MAPS_KEY
from ace.constants import MAX_PER_PAGE, USER_TYPE_CANDIDATE, USER_TYPE_EMPLOYER, USER_TYPE_SUPER, DEFAULT_VIDEO
from joblistings.models import Job, JobPDFDescription
from joblistings.forms import JobForm, AdminAddRemoveJobPermission, FilterApplicationForm
from companies.models import Company
from accounts.models import Employer, Candidate
from django_sendfile import sendfile
from jobapplications.models import JobApplication
from django.db.models import Q
import json as simplejson
from datetime import datetime, timedelta
import re
from django.utils import timezone
from django.db import transaction
from ace.settings import GOOGLE_MAPS_KEY

# Create your views here.
@transaction.atomic
def job_search(request, searchString="", *args, **kwargs):
    context = {}
    jobApps = None
    form = FilterApplicationForm()

    args = []
    page = 1

    
    filterClasses = []
    filterHTML = []
    sortOrder = '-created_at'
    query = Q()

    if request.method == 'POST':
        form = FilterApplicationForm(request.POST, page=request.POST.get('page'))        
        page = int(form.fields['page'].initial)
        import sys
        print(page, file=sys.stderr)
        if 'filter' in request.POST or 'nextPage' in request.POST or 'prevPage' in request.POST:
            context['filterClasses'] = simplejson.dumps(form.getSelectedFilterClassAsList())
            context['filterHTML'] = simplejson.dumps(form.getSelectedFilterHTMLAsList())
        
        keywords = request.POST['keyword']

        queries = keywords.split(" ")
        for q in queries:
            q1 = Q(company__name__icontains=q)
            q2 = Q(description__icontains=q)
            q3 = Q(title__icontains=q)
            q4 = Q(responsabilities__icontains=q)
            combined_q = q1 | q2 | q3 | q4
            query &= (combined_q)
            
        filterSet = form.getSelectedFilterAsSet()
        newSet = set()
        for element in filterSet:
            newSet.add(re.sub('[^A-Za-z0-9 ]', '', element))
        filterSet = newSet
        #if not request.user.is_authenticated or request.user.user_type != USER_TYPE_SUPER:
            #query &=(Q(status= "Approved") | Q(status="Interviewing") | Q(status="Filled") | Q(status="Partially Filled") | Q(status="Closed"))

        if "Last 24 hours" in filterSet:
            query &= Q(created_at__gte=timezone.now()-timedelta(days=1))
        if "Last 7 days" in filterSet:
            query &= Q(created_at__gte=timezone.now()-timedelta(days=7))
        if "Last 14 days" in filterSet:
            query &= Q(created_at__gte=timezone.now()-timedelta(days=14))
        if "Last month" in filterSet:
            query &= Q(created_at__gte=timezone.now()-timedelta(days=30))
        if "Last 3 months" in filterSet:
            query &= Q(created_at__gte=timezone.now()-timedelta(days=90))
        if 'Oldest First' in filterSet:
            sortOrder = 'created_at'
        if "Active" in filterSet:
            query &= (Q(status="Approved")  | Q(status="Interviewing"))
        if "Closed" in filterSet:
            query &= (Q(status="Filled") | Q(status="Partially Filled") | Q(status="Closed"))
        if "Pending Approval" in filterSet:
            query &= Q(status="Pending Review")
        if "Approved" in filterSet:
            query &= (Q(status= "Submitted") | Q(status="Not Selected"))
        if "Not Approved" in filterSet:
            query &= Q(status="Not Approved")
        if "Interviewing" in filterSet:
            query &= (Q(status= "Interviewing") | Q(status="Ranked") | Q(status= "1st"))
        if "Matched" in filterSet:
            query &= Q(status="Matched")
        if "Not Matched/Closed" in filterSet:
            query &= (Q(status= "Not Matched") | Q(status="Closed"))
        if form["program"].value() != None and form["program"].value() != "ANY":
            query &= (Q(category__icontains= form["program"].value()))


        qs = Job.objects.filter(query).order_by(sortOrder).distinct()
        queryset = qs
 
        context['joblist'] = queryset
        context['job_num'] = str(len(queryset))

        context["form"] = form

        maxCount = len(context['joblist'])

        low = max((page-1)*MAX_PER_PAGE, 0)
        high = min(page*MAX_PER_PAGE, maxCount)

        maxPage = int(maxCount/MAX_PER_PAGE)
        minPage = 1

        if page > maxPage:
            page = maxPage
            form.fields['page'].initial = maxPage
        
        if page < minPage:
            page = minPage
            form.fields['page'].initial = minPage
        context['form'] = form
        low = max((page-1)*MAX_PER_PAGE, 0)
        high = min(page*MAX_PER_PAGE, maxCount)

        context['pageLow'] = low+1
        context['pageHigh'] = high
        context['pageRange'] = maxCount
    
        context['joblist'] = context['joblist'][low:high]

        if page == 1:
            context['hideLow'] = True
        if page == maxPage:
            context['hideHigh'] = True
        return render(request, 'job-listing.html', context)

    if not request.user.is_authenticated or request.user.user_type != USER_TYPE_SUPER:
        query &=(Q(status= "Approved") | Q(status="Interviewing") | Q(status="Filled") | Q(status="Partially Filled") | Q(status="Closed"))
    args.append(query)
    queryset = Job.objects.filter(*args).order_by(sortOrder).distinct()

    context['joblist']= queryset
    context['job_num']= str(len(queryset))
    
    maxCount = len(context['joblist'])

    low = max((page-1)*MAX_PER_PAGE, 0)
    high = min(page*MAX_PER_PAGE, maxCount)

    maxPage = int(maxCount/MAX_PER_PAGE)
    minPage = 1

    if page > maxPage:
        page = maxPage
        form.fields['page'].initial = maxPage
    
    if page < minPage:
        page = minPage
        form.fields['page'].initial = minPage
    context['form'] = form
    low = max((page-1)*MAX_PER_PAGE, 0)
    high = min(page*MAX_PER_PAGE, maxCount)

    context['pageLow'] = low+1
    context['pageHigh'] = high
    context['pageRange'] = maxCount

    context['joblist'] = context['joblist'][low:high]

    if page == 1:
        context['hideLow'] = True
    if page == maxPage:
        context['hideHigh'] = True

    return render(request, 'job-listing.html', context)


def job_details(request, pk=None, *args, **kwargs):
    instance = get_object_or_404(Job, pk=pk)

    context = {
        'object': instance,
        'pk': pk
    }


    context["similarJobs"] = Job.objects.filter(company=instance.company).order_by("-created_at").distinct()[:]
    if instance.company.videoLink != DEFAULT_VIDEO:
        context["video"] = True

    jobPDF = JobPDFDescription.objects.filter(job=pk)

    if (jobPDF):
        context["download"] = pk
        context["downloadPk"] = jobPDF[0].pk

    if request.user.is_authenticated and request.user.user_type == USER_TYPE_SUPER:
        if request.method == 'POST':
            if request.POST.get('Not Approved'):
                instance.status = "Not Approved"
                instance.save()
            if request.POST.get('Approved'):
                instance.status = "Approved"
                instance.save()
            if request.POST.get('Add'):
                if request.POST.get("addEmployer") != "Add Permission":
                    instance.jobAccessPermission.add(int(request.POST.get("addEmployer")))
            if request.POST.get('Remove'):
                if request.POST.get("removeEmployer") != "Remove Permission":
                    instance.jobAccessPermission.remove(int(request.POST.get("removeEmployer")))

        form = AdminAddRemoveJobPermission(jobId=pk)
        context["form"] = form
        context["googleMapsKey"] = GOOGLE_MAPS_KEY

    return render(request, "job-details.html", context)

def post_job(request,  *args, **kwargs):
    context = {}
    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please register with ACE first"
        return HttpResponseRedirect('/login')
    else:
        
        if request.user.user_type == USER_TYPE_CANDIDATE:
            request.session['info'] = "You are logged in as a candidate. Only employers can access this page"
            return  HttpResponseRedirect('/')

        if not request.user.is_email_confirmed:
            return HttpResponseRedirect('/activate')

    if (request.method == "POST"):
        form = JobForm(user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            job = form.save()
            

            if request.user.user_type == USER_TYPE_EMPLOYER:
                job.jobAccessPermission.add(Employer.objects.get(user=request.user)) 
                job.save()

            if request.user.user_type == USER_TYPE_SUPER:
                job.status = "Approved"
                job.save()
                
            job_pk = job.pk
        
        
            return HttpResponseRedirect('/job-details/' + str(job_pk))
        
        else:
            context['form'] = form
            context['googleMapsKey'] = GOOGLE_MAPS_KEY
            context['showError'] = True
            return render(request, "employer-dashboard-post-job.html", context)


    
    jobForm = JobForm(user=request.user)
    context['form'] = jobForm
    context['googleMapsKey'] = GOOGLE_MAPS_KEY

    return render(request, "employer-dashboard-post-job.html", context)


def manage_jobs(request, searchString=""):
    orderby = '-created_at'

    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login first"
        return HttpResponseRedirect('/login')

    if searchString:
            searchWords = searchString.split("&")
    else:
        searchWords = []

    search = {}

    for searchWord in searchWords:
        pair = searchWord.split("=")
        if len(pair) == 2:
            search[pair[0]] = pair[1]

    user = request.user

    notifications = []
    if "chronological" in search:   
        orderby = '-created_at'
    if "alphabetical" in search:
        orderby = '-title'
    if "company" in search:
        orderby = '-company__name'

    if request.user.user_type == USER_TYPE_SUPER:
        
        jobQuery = Job.objects.order_by(orderby).all()

        jobs = {}

        jobs = []
        for job in jobQuery:
            obj = {}

            obj['job'] = job
            obj['count'] = JobApplication.objects.filter(job=job).count()
            jobs.append(obj)

        context = {
                    "jobs" : jobs,
                    'user' : request.user,
                }

    if request.user.user_type == USER_TYPE_EMPLOYER:

        jobQuery = Job.objects.filter(jobAccessPermission = Employer.objects.get(user=request.user)).order_by(orderby)

        query1 = ~Q(status="Pending Review")
        query2 = ~Q(status="Not Approved")


        jobs = []
        for job in jobQuery:
            obj = {}

            obj['job'] = job

            obj['count'] = JobApplication.objects.filter(query1,query2,job=job).count()
            
            jobs.append(obj)


        context = {
                    "jobs" : jobs,
                    'user' : request.user,
                }

    if request.user.user_type == USER_TYPE_CANDIDATE:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: This page is only accessible to employers"
        return HttpResponseRedirect('/')
    context["newMessageCount"] = len(request.user.notifications.unread())
    return render(request, "dashboard-manage-job.html", context)

def download_jobPDF(request, pk):
    download = get_object_or_404(JobPDFDescription, job=pk)
    return sendfile(request, "/" + download.descriptionFile.path)
