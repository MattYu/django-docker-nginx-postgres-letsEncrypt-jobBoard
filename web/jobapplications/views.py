from django.shortcuts import render, get_object_or_404
from joblistings.models import Job
from jobapplications.models import JobApplication, Resume, CoverLetter, Education, Experience, Ranking, SupportingDocument
from jobapplications.forms import ApplicationForm, resumeUpload, FilterApplicationForm
from django_sendfile import sendfile
import uuid
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from ace.constants import USER_TYPE_EMPLOYER, USER_TYPE_CANDIDATE
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from io import BytesIO, StringIO
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import requests

from ace.constants import FILE_TYPE_RESUME, FILE_TYPE_COVER_LETTER, FILE_TYPE_TRANSCRIPT, FILE_TYPE_OTHER, USER_TYPE_SUPER, USER_TYPE_CANDIDATE, USER_TYPE_EMPLOYER

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django_sendfile import sendfile
from accounts.models import User, Candidate, Employer, Language, PreferredName
import uuid
from django.db import transaction
from django.db.models import Q

import json as simplejson
from datetime import datetime, timedelta
from django.core.files.storage import FileSystemStorage

#u = uuid.uuid4()
#u.hex

# Create your views here.
def add_resume(request, pk= None, *args, **kwargs):
    
    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login before applying to a job"
        return HttpResponseRedirect('/login')
    else:
        if request.user.user_type != USER_TYPE_CANDIDATE:
            request.session['info'] = "Only candidates can access this page"
            return  HttpResponseRedirect('/')

        if not request.user.is_email_confirmed:
            return HttpResponseRedirect('/activate')

        jobApplication = JobApplication.objects.filter(job__pk=pk, candidate=Candidate.objects.get(user=request.user)).count()

        if jobApplication !=0:
            request.session['info'] = "You already applied to this job"
            jobApplication = JobApplication.objects.get(job__pk=pk, candidate=Candidate.objects.get(user=request.user))
            return HttpResponseRedirect('/jobApplicationDetails/' + str(jobApplication.pk) + "/")

    
    instance = get_object_or_404(Job, pk=pk)

    if instance.status == "Close" or instance.status == "Filled" or instance.status == "Partially Filled":
        request.session['info'] = "Job closed"
        return HttpResponseRedirect('/')
    context = {'job': instance}
    
    if (request.method == 'POST'):
        form = ApplicationForm(
            request.POST, 
            request.FILES,
            extra_edu_count=request.POST.get('extra_edu_count'), 
            extra_exp_count=request.POST.get('extra_exp_count'), 
            extra_doc_count=request.POST.get('extra_doc_count'),
            initWithHistory=False,
            user=request.user
            )
        #request.session['form'] = form.as_p()

        if 'Apply' in request.POST:
            context["showError"] = True

            if form.is_valid():
                form.clean()
                jobApplication = form.save(instance, request.user)


                return HttpResponseRedirect('/jobApplications/')
    else:
        form = ApplicationForm(extra_edu_count=1, extra_exp_count=1, extra_doc_count=0, user=request.user, initWithHistory=True)
    context['form'] = form
    return render(request, "add-resume.html", context)


def download_test(request, pk):
    download = get_object_or_404(Job, pk=pk)
    return sendfile(request, "/" + download.company.image.path)

@transaction.atomic
def browse_job_applications(request, searchString = "", jobId= -1):
    context = {}
    jobApplications = None
    form = FilterApplicationForm()
    query = Q()

    filterClasses = []
    filterHTML = []
    sortOrder = '-created_at'

    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login before applying to a job"
        return HttpResponseRedirect('/login')


    if request.user.user_type == USER_TYPE_SUPER:
        kwargs = {}
        if jobId != None:
            query = Q(job__pk=jobId)
            try:
                context["job"] = Job.objects.get(pk=jobId)
            except:
                context["job"] = []


    if request.user.user_type == USER_TYPE_EMPLOYER:
        query = Q(job__jobAccessPermission=Employer.objects.get(user=request.user))
        query &= ~Q(status="Pending Review")
        query &= ~Q(status="Not Approved")
        
        if jobId != None:
            query &= Q(job__pk=jobId)
            try:
                context["job"] = Job.objects.get(pk=jobId)
            except:
                context["job"] = []


    if request.user.user_type == USER_TYPE_CANDIDATE:
        query = Q(candidate= Candidate.objects.get(user=request.user))

    if (request.method == 'POST'):
        form = FilterApplicationForm(request.POST)        

        if 'filter' in request.POST:
            context['filterClasses'] = simplejson.dumps(form.getSelectedFilterClassAsList())
            context['filterHTML'] = simplejson.dumps(form.getSelectedFilterHTMLAsList())
            #for ob in request.POST.get('selected_filter'):
            #    print(ob)
            #print("test***")

    # Applying filter value here
    filterSet = form.getSelectedFilterAsSet()

    if searchString:
        searchWords = searchString.split("&")
    else:
        searchWords = []

    search = {}

    for searchWord in searchWords:
        pair = searchWord.split("=")
        if len(pair) == 2:
            search[pair[0]] = pair[1]


    try:
        if "Last 24 hours" in filterSet:
            query &= Q(created_at__gte=datetime.now()-timedelta(days=1))
        if "Last 7 days" in filterSet:
            query &= Q(created_at__gte=datetime.now()-timedelta(days=7))
        if "Last 14 days" in filterSet:
            query &= Q(created_at__gte=datetime.now()-timedelta(days=14))
        if "Last month" in filterSet:
            query &= Q(created_at__gte=datetime.now()-timedelta(days=30))
        if "Last 3 months" in filterSet:
            query &= Q(created_at__gte=datetime.now()-timedelta(days=90))
        if form["companyName"].value() != None and form["companyName"].value() != "":
                query &= Q(job__company__name__icontains=form["companyName"].value())
        if request.user.user_type != USER_TYPE_CANDIDATE:
            if form["firstName"].value() != None and form["firstName"].value() != "":
                query &= (Q(firstName__icontains= form["firstName"].value()) | Q(candidate__user__preferredName__contains=form["firstName"].value()))
            if form["lastName"].value() != None and form["lastName"].value() != "":
                query &= Q(lastName__icontains= form["lastName"].value())
            if form["email"].value() != None and form["email"].value() != "":
                query &= Q(candidate__user__email__icontains=form["email"].value())
            if form["studentId"].value() != None and form["studentId"].value() != "":
                query &= Q(candidate__studentID__icontains=form["studentId"].value())
            
            if form["gpa_min"].value() != None and form["gpa_min"].value() != "1.7" :
                query &= Q(candidate__gpa__gte = float(form["gpa_min"].value()))
            if form["gpa_max"].value() != None and form["gpa_max"].value() != "4.3" :
                query &= Q(candidate__gpa__lte = float(form["gpa_max"].value()))
        if form["program"].value() != None and form["program"].value() != "ANY":
            query &= Q(candidate__program= form["program"].value())
        if 'Oldest First' in filterSet:
            sortOrder = 'created_at'
        if "Pending Review" in filterSet:
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
    except Exception as e:
        import sys
        print(e, file=sys.stderr)
        pass
    if 'oldest' in searchString:
        import sys
        sortOrder = 'created_at'

    jobApplications = JobApplication.objects.filter(query).order_by(sortOrder)
    context["jobApplications"] = jobApplications
    context["form"] = form

    if (request.method == 'POST'):
        if 'pdf' in request.POST:
            '''
        if fileType == (FILE_TYPE_RESUME):
            fileId = Resume.objects.get(JobApplication__id=applicationId).id
            resume = Resume.objects.get(id=fileId).resume
            filePath = resume.path


        if fileType == (FILE_TYPE_COVER_LETTER):
            fileId = CoverLetter.objects.get(JobApplication__id=applicationId).id
            coverLetter = CoverLetter.objects.get(id=fileId).coverLetter
            filePath = coverLetter.path
 

        if fileType == (FILE_TYPE_TRANSCRIPT):
            candidateId = JobApplication.objects.get(id=applicationId).candidate.id
            transcript = Candidate.objects.get(id=candidateId).transcript
            filePath = transcript.path
            

        if fileType == (FILE_TYPE_OTHER):
            supportingDocument = SupportingDocument.objects.filter(JobApplication=applicationId, pk=supportID)[0]
            if not supportingDocument:
                return HttpResponse('File ID does not exist')
            document = supportingDocument
            filePath = document.path
            '''

            # PDF download request
            response = HttpResponse()
            response['Content-Disposition'] = 'attachment; filename=downloadApplications.pdf'
            writer = PdfFileWriter()
            # Change to https in prod (although django should automatically force https if settings.py is configured corretly in prod)
            # base_url = "http://" + str(get_current_site(request).domain)  + "/getFile"
        
            #User.objects.filter(id=request.user.id).update(protect_file_temp_download_key=str(uuid.uuid4().hex))
            #token = downloadProtectedFile_token.make_token(request.user)

            merger = PdfFileMerger()

            for application in jobApplications:
                #uid = urlsafe_base64_encode(force_bytes(request.user.pk))
                #candidateId = urlsafe_base64_encode(force_bytes(application.candidate.pk))

                fileId = Resume.objects.get(JobApplication__id=application.pk).id
                resume = Resume.objects.get(id=fileId).resume
                filePath = resume.path

                fs = FileSystemStorage()

                try:
                    if fs.exists(filePath):
                        with fs.open(filePath, 'rb') as doc:
                            merger.append(PdfFileReader(doc))
                except:
                    pass

                fileId = CoverLetter.objects.get(JobApplication__id=application.pk).id
                coverLetter = CoverLetter.objects.get(id=fileId).coverLetter
                filePath = coverLetter.path
                
                try:
                    if fs.exists(filePath):
                        with fs.open(filePath, 'rb') as doc:
                            merger.append(PdfFileReader(doc))
                except:
                    pass

                candidateId = JobApplication.objects.get(id=application.pk).candidate.id
                transcript = Candidate.objects.get(id=candidateId).transcript
                filePath = transcript.path

                try:
                    if fs.exists(filePath):
                        with fs.open(filePath, 'rb') as doc:
                            merger.append(PdfFileReader(doc))
                except:
                    pass



                supportingDocuments = SupportingDocument.objects.filter(JobApplication=application.pk)

                for supportingDoc in supportingDocuments:
                    filePath = supportingDoc.document.path
                    try:
                        if fs.exists(filePath):
                            with fs.open(filePath, 'rb') as doc:
                                merger.append(PdfFileReader(doc))
                    except:
                        pass
                
            outputStream = BytesIO()
            merger.write(outputStream)
            response.write(outputStream.getvalue())

            #User.objects.filter(id=request.user.id).update(protect_file_temp_download_key="")
            return response

    context["newMessageCount"] = len(request.user.notifications.unread())
    
    return render(request, "dashboard-manage-applications.html", context)


def view_application_details(request, pk):
    context = {}

    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login before applying to a job"
        return HttpResponseRedirect('/login')

    if request.user.user_type == USER_TYPE_SUPER:
        jobApplication = get_object_or_404(JobApplication, id=pk)

        context = {"jobApplication" : jobApplication}

        if request.method == 'POST':
            if request.POST.get('Approved'):
                jobApplication.status= "Submitted"
                jobApplication.save()
            if request.POST.get('Reject'):
                jobApplication.status= "Not Approved"
                jobApplication.save()
            if request.POST.get('Interview'):
                ranking = Ranking()
                ranking.jobApplication = jobApplication
                ranking.job = jobApplication.job
                ranking.candidate = jobApplication.candidate
                ranking.save()
                jobApplication.status= "Interviewing"
                jobApplication.job.status= "Interviewing"
                jobApplication.save()

        if jobApplication.status == "Pending Review" or jobApplication.status== "Not Approved":
            context['showButton'] = True
        
        if jobApplication.status == "Submitted":
            context['showInterview'] = True


    if request.user.user_type == USER_TYPE_EMPLOYER:
        query = Q(job__jobAccessPermission = Employer.objects.get(user=request.user))
        query &= ~Q(status="Pending Review")
        query &= ~Q(status="Not Approved")
        query &= Q(id=pk)

        jobApplication = get_object_or_404(JobApplication, query)

        context = {"jobApplication" : jobApplication}

        if request.method == 'POST':
            if request.POST.get('Approved'):
                ranking = Ranking()
                ranking.jobApplication = jobApplication
                ranking.job = jobApplication.job
                ranking.candidate = jobApplication.candidate
                ranking.save()
                jobApplication.status= "Interviewing"
                jobApplication.job.status= "Interviewing"
                jobApplication.save()

            if request.POST.get('Reject'):
                jobApplication.status= "Not Selected"
                jobApplication.save()

        if jobApplication.status == "Submitted" or jobApplication.status== "Not Selected":
            context['showButton'] = True


    if request.user.user_type == USER_TYPE_CANDIDATE:
        jobApplication = get_object_or_404(JobApplication,id=pk, candidate=Candidate.objects.get(user=request.user))

        context = {"jobApplication" : jobApplication}

    educations = Education.objects.filter(JobApplication=jobApplication).all()

    experience = Experience.objects.filter(JobApplication=jobApplication).all()



    supportingDocuments = SupportingDocument.objects.filter(JobApplication=jobApplication)

    languages = Language.objects.filter(user=jobApplication.candidate.user)
    preferredName = None
    if request.user.preferredName != "":
        preferredName = request.user.preferredName
        context['preferredName'] = preferredName

    context['educations'] = educations
    context['experience'] = experience
    context['languages'] = languages

    if supportingDocuments:
        context['supportingDocuments'] = supportingDocuments

    context['user'] = request.user

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

    return render(request, "application-details.html", context)

    
def get_protected_file(request, uid, candidateId, filetype, fileid, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None:
        #and downloadProtectedFile_token.check_token(user, token):

        # Future proof section intentionally left blank. Web currently has not need for this functionality.
        # Could enable valid users to access protected file with a tokenized link. 
        
        return HttpResponse('Invalid permission token')


def get_protected_file_withAuth(request, fileType, applicationId, supportID=""):

    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login before applying to a job"
        return HttpResponseRedirect('/login')

    if request.user.user_type == USER_TYPE_SUPER:

        if fileType == (FILE_TYPE_RESUME):
            fileId = Resume.objects.get(JobApplication__id=applicationId).id
            resume = Resume.objects.get(id=fileId).resume
            filePath = resume.path


        if fileType == (FILE_TYPE_COVER_LETTER):
            fileId = CoverLetter.objects.get(JobApplication__id=applicationId).id
            coverLetter = CoverLetter.objects.get(id=fileId).coverLetter
            filePath = coverLetter.path
 

        if fileType == (FILE_TYPE_TRANSCRIPT):
            candidateId = JobApplication.objects.get(id=applicationId).candidate.id
            transcript = Candidate.objects.get(id=candidateId).transcript
            filePath = transcript.path
            

        if fileType == (FILE_TYPE_OTHER):
            supportingDocument = SupportingDocument.objects.filter(JobApplication=applicationId, pk=supportID)[0]
            if not supportingDocument:
                return HttpResponse('File ID does not exist')
            document = supportingDocument.document
            filePath = document.path

        return sendfile(request, "/" + filePath)

    if request.user.user_type == USER_TYPE_EMPLOYER:
        jobApplications = JobApplication.objects.filter(job__jobAccessPermission=Employer.objects.get(user=request.user), id=applicationId).count()
        
        if jobApplications == 0:
            return HttpResponse('Invalid permission token')

        if fileType == (FILE_TYPE_RESUME):
            fileId = Resume.objects.get(JobApplication__id=applicationId).id
            resume = Resume.objects.get(id=fileId).resume
            filePath = resume.path


        if fileType == (FILE_TYPE_COVER_LETTER):
            fileId = CoverLetter.objects.get(JobApplication__id=applicationId).id
            coverLetter = CoverLetter.objects.get(id=fileId).coverLetter
            filePath = coverLetter.path
 

        if fileType == (FILE_TYPE_TRANSCRIPT):
            candidateId = JobApplication.objects.get(id=applicationId).candidate.id
            transcript = Candidate.objects.get(id=candidateId).transcript
            filePath = transcript.path
            

        if fileType == (FILE_TYPE_OTHER):
            supportingDocument = SupportingDocument.objects.filter(JobApplication=applicationId, pk=supportID)[0]
            if not supportingDocument:
                return HttpResponse('File ID does not exist')
            document = supportingDocument.document
            filePath = document.path

        return sendfile(request, "/" + filePath)

    if request.user.user_type == USER_TYPE_CANDIDATE:
        jobApplications = JobApplication.objects.filter(candidate=Candidate.objects.get(user=request.user), id=applicationId).count()


        if jobApplications == 0:
            return HttpResponse('Invalid permission token')

        if fileType == (FILE_TYPE_RESUME):
            fileId = Resume.objects.get(JobApplication__id=applicationId).id
            resume = Resume.objects.get(id=fileId).resume
            filePath = resume.path


        if fileType == (FILE_TYPE_COVER_LETTER):
            fileId = CoverLetter.objects.get(JobApplication__id=applicationId).id
            coverLetter = CoverLetter.objects.get(id=fileId).coverLetter
            filePath = coverLetter.path
 

        if fileType == (FILE_TYPE_TRANSCRIPT):
            candidateId = JobApplication.objects.get(id=applicationId).candidate.id
            transcript = Candidate.objects.get(id=candidateId).transcript
            filePath = transcript.path
            

        if fileType == (FILE_TYPE_OTHER):
            supportingDocument = SupportingDocument.objects.filter(JobApplication=applicationId, pk=supportID)[0]
            if not supportingDocument:
                return HttpResponse('File ID does not exist')
            document = supportingDocument.document
            filePath = document.path
        return sendfile(request, "/" + filePath)     
    else:
        return HttpResponse('Invalid permission token')
