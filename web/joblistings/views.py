#from django.views import ListView
from django.shortcuts import render, get_object_or_404
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q


from ace.constants import USER_TYPE_CANDIDATE, USER_TYPE_EMPLOYER, USER_TYPE_SUPER
from joblistings.models import Job, JobPDFDescription
from joblistings.forms import JobForm, AdminAddRemoveJobPermission
from companies.models import Company
from accounts.models import Employer, Candidate
from django_sendfile import sendfile
from jobapplications.models import JobApplication
from django.db.models import Q


# Create your views here.
def job_search(request, *args, **kwargs):
    if request.method == 'POST':
        keywords = request.POST['keyword']

        args = []
        queries = keywords.split(" ")
        for query in queries:
            q1 = Q(company__name__icontains=query)
            q2 = Q(description__icontains=query)
            q3 = Q(title__icontains=query)
            q4 = Q(responsabilities__icontains=query)
            combined_q = q1 | q2 | q3 | q4
            args.append(combined_q)

        qs = Job.objects.filter(*args).distinct()
        qs = list(set(qs))

        queryset = []
        for q in qs:
            queryset.append(q)
 
        context = {
            'joblist': queryset,
            'job_num': str(len(queryset))
        }

        return render(request, 'job-listing.html', context)

    return HttpResponseRedirect("/")


def job_details(request, pk=None, *args, **kwargs):
    instance = get_object_or_404(Job, pk=pk)

    context = {
        'object': instance,
        'pk': pk
    }

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

    return render(request, "job-details.html", context)

def post_job(request,  *args, **kwargs):

    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please register with ACE first"
        return HttpResponseRedirect('/login')
    else:
        if request.user.user_type == USER_TYPE_CANDIDATE:
            request.session['info'] = "You are logged in as a candidate. Only employers can access this page"
            return  HttpResponseRedirect('/')

    if (request.method == "POST"):
        form = JobForm(user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.clean()
            job = form.save()

            if request.user.user_type == USER_TYPE_EMPLOYER:
                job.jobAccessPermission.add(Employer.objects.get(user=request.user)) 
                job.save()
                

            job_pk = job.pk
            
            

            return HttpResponseRedirect('/job-details/' + str(job_pk))

    
    jobForm = JobForm(user=request.user)
    context = {'form' : jobForm}

    return render(request, "employer-dashboard-post-job.html", context)

def manage_jobs(request):
    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login first"
        return HttpResponseRedirect('/login')


    if request.user.user_type == USER_TYPE_SUPER:
        
        jobQuery = Job.objects.all()

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

        jobQuery = Job.objects.filter(jobAccessPermission = Employer.objects.get(user=request.user))

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

    return render(request, "dashboard-manage-job.html", context)

def download_jobPDF(request, pk):
    download = get_object_or_404(JobPDFDescription, job=pk)
    return sendfile(request, download.descriptionFile.path)

