from django.shortcuts import render, get_object_or_404
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from jobapplications.models import JobApplication, Ranking
from django.db.models import Q
from joblistings.models import Job
from ace.constants import USER_TYPE_CANDIDATE, USER_TYPE_EMPLOYER, USER_TYPE_SUPER
from accounts.models import Employer, Candidate
from jobmatchings.forms import EmployerRankingForm, CandidateRankingForm

from jobmatchings.models import MatchingHistory, Match
from matching import games as ranking
from django.db import transaction
from datetime import datetime, timedelta
from django.utils import timezone

from django.core.mail import EmailMessage
from django.core import mail
from django.contrib.sites.shortcuts import get_current_site
from notifications.signals import notify
from django.template.loader import render_to_string
from announcements.models import MatchingMessage, RankingMessage

# Create your views here.
@transaction.atomic
def employer_view_rankings(request, jobId= None):
    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login first"
        return HttpResponseRedirect('/login')


    if request.user.user_type == USER_TYPE_SUPER:

        if jobId == None:
        
            jobQuery = Job.objects.all()

            jobs = {}

            jobs = []

            query1 = Q(status="Interviewing")
            query2 = Q(status="Ranked")
            query3 = Q(status="1st")

            for job in jobQuery:
                obj = {}

                obj['job'] = job
                obj['count'] = JobApplication.objects.filter(query1|query2|query3, job=job).count()
                jobs.append(obj)

            context = {
                        "jobs" : jobs,
                        'user' : request.user,
                    }

        else:
            jobQuery = get_object_or_404(Job, id=jobId)

            context = {
                        "job" : jobQuery,
                        }

            if (request.method == "POST"):
                for rank in Ranking.objects.filter(job__id=jobId).all():
                    if request.POST.get(str(rank.id)):
                        rank.employerRank = int(request.POST.get(str(rank.id)))
                        rank.save()



            form = EmployerRankingForm(jobId=jobId)

            context["form"] = form

    if request.user.user_type == USER_TYPE_EMPLOYER:

        if jobId == None:
            jobQuery = Job.objects.filter(jobAccessPermission = Employer.objects.get(user=request.user))

            query1 = Q(status="Interviewing")
            query2 = Q(status="Ranked")
            query3 = Q(status="1st")


            jobs = []
            for job in jobQuery:
                obj = {}

                obj['job'] = job

                obj['count'] = JobApplication.objects.filter(query1|query2|query3,job=job).count()
                
                jobs.append(obj)

            context = {
                        "jobs" : jobs,
                        'user' : request.user,
                        }
        else:
            jobQuery = get_object_or_404(Job, id=jobId, jobAccessPermission = Employer.objects.get(user=request.user))

            if (request.method == "POST"):
                for rank in Ranking.objects.filter(job__id=jobId).all():
                    if request.POST.get(str(rank.id)):
                        rank.employerRank = int(request.POST.get(str(rank.id)))
                        rank.save()

            context = {
                        "job" : jobQuery,
                        }

            form = EmployerRankingForm(jobId=jobId)

            context["form"] = form

    if request.user.user_type == USER_TYPE_CANDIDATE:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: This page is only accessible to employers"
        return HttpResponseRedirect('/')
    context["newMessageCount"] = len(request.user.notifications.unread())
    return render(request, "dashboard-ranking.html", context)

@transaction.atomic
def candidate_view_rankings(request):
    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login first"
        return HttpResponseRedirect('/login')


    if request.user.user_type == USER_TYPE_CANDIDATE:

        if (request.method == "POST"):
            for rank in Ranking.objects.filter(candidate__id=Candidate.objects.get(user=request.user).id, is_closed=False).all():
                if request.POST.get(str(rank.id)):
                    rank.candidateRank = int(request.POST.get(str(rank.id)))
                    rank.save()

        form = CandidateRankingForm(candidateId=Candidate.objects.get(user=request.user).id)

        context = {
            "form" : form,
            }
    context["newMessageCount"] = len(request.user.notifications.unread())
    context["announcements"] = RankingMessage.objects.filter().all()
    return render(request, "dashboard-ranking-candidate.html", context)

@transaction.atomic
def admin_matchmaking(request):
    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login first"
        return HttpResponseRedirect('/login')


    if request.user.user_type == USER_TYPE_SUPER:
        context = {}
        if (request.method == "POST"):

            if request.POST.get("closeEmp"):

                for rank in Ranking.objects.filter(is_ranking_open_for_employer=True):
                    rank.is_ranking_open_for_employer = False
                    rank.is_ranking_open_for_candidate = True
                    rank.save()
                context["message"] = "1 - Success. Employer Ranking Closed. Candidate Ranking Opened."

            if request.POST.get("closeCan"):
                for rank in Ranking.objects.filter(is_ranking_open_for_candidate=True):
                    rank.is_ranking_open_for_candidate = False
                    rank.save()

                context["message"] = "2 - Success. Candidate Ranking Closed. All Rankings are now locked."

            if request.POST.get("MATCH"):
                matchingHistory = MatchingHistory()
                matchingHistory.save()

                for rank in Ranking.objects.filter(is_closed=False):
                    if rank.candidateRank == 1000 or rank.candidateRank == 999 or rank.employerRank == 1000 or rank.employerRank == 999:
                        rank.status = "Not Matched"
                        rank.jobApplication.status = "Not Matched"
                        rank.is_closed = True
                        rank.jobApplication.save()
                        rank.save()

                    if rank.candidateRank == 1 and rank.employerRank == 1:
                        rank.candidateRank = 0
                        rank.employerRank = 0
                        rank.save()


                employer_prefs = {}
                capacities = {}

                for rank in Ranking.objects.filter(~Q(status="Matched") & ~Q(status="Not Matched")).order_by('employerRank'):
                    jobId = rank.jobApplication.job.id
                    job = rank.jobApplication.job

                    if jobId not in employer_prefs:
                        employer_prefs[jobId] = [rank.candidate.id]
                        capacities[jobId] = job.vacancy
                    else:
                        employer_prefs[jobId].append(rank.candidate.id)
                
                candidate_prefs = {}
                for rank in Ranking.objects.filter(~Q(status="Matched") & ~Q(status="Not Matched")).order_by('candidateRank'):
                    candidate = rank.candidate.id

                    if candidate not in candidate_prefs:
                        candidate_prefs[candidate] = [rank.jobApplication.job.id]
                    else:
                        candidate_prefs[candidate].append(rank.jobApplication.job.id)

                match = ranking.HospitalResident.create_from_dictionaries( candidate_prefs, employer_prefs, capacities)

                matchResult = match.solve(optimal="resident")

                matchingHistory = MatchingHistory()
                matchingHistory.save()

                for jobObj in matchResult:
                    for candidate in matchResult[jobObj]:
                        match = Match()
                        match.candidate = Candidate.objects.get(id=int(candidate.name))
                        job = Job.objects.get(id=int(jobObj.name))
                        match.job = job
                        match.jobApplication = JobApplication.objects.filter(candidate=Candidate.objects.get(id=int(candidate.name)), job= job).first()
                        match.save()
                        #match.jobApplication.status = "Matched"
                        #match.jobApplication.save()

                        matchingHistory.matches.add(match)
                        matchingHistory.save()

                        job.vacancy -= 1
                        job.filled += 1
                        job.save()

                        if job.vacancy == 0:
                            job.status = "Filled"
                            job.save()
                        if job.vacancy !=0 and job.filled != 0:
                            job.status = "Partially Filled"
                            job.save()                           

                for rank in Ranking.objects.filter(is_closed=False):
                    if Match.objects.filter(jobApplication=rank.jobApplication).count() == 0:
                        rank.status = "Not Matched"
                        rank.is_closed = True
                        rank.save()
                    else:
                        rank.status = "Matched"
                        rank.is_closed = True
                        rank.save()
                context["message"] = "3 - Success. Matches generated in favour of candidates. Matches are currently only visible to you (admin). Please review them. The next step notify all candidates and employers. Note that step 4 can be slow. This is normal behavior since sending emails takes time."

            if request.POST.get("open"):
                connection = mail.get_connection()
                try:
                    connection.open()
                except Exception as e:
                    import sys
                    print(e, file=sys.stderr)


                messages = []

                for rank in Ranking.objects.filter(is_closed=False):
                    if Match.objects.filter(jobApplication=rank.jobApplication).count() == 0:
                        rank.jobApplication.status = "Not Matched"
                        rank.is_closed = True
                        rank.save()
                        rank.jobApplication.save()
                    else:
                        rank.jobApplication.status = "Matched"
                        rank.is_closed = True
                        rank.save()
                        rank.jobApplication.save()

                for match in Match.objects.filter(isOpenToPublic=False).all():
                    #Create message for employer
                    #import sys
                    #print("Sending messages??", file=sys.stderr)
                    current_site = get_current_site(request)
                    # Step 1: find the email(s) of the job owner(s) in the system
                    email_to = set()
                    
                    job = match.jobApplication.job
                    for employer in match.jobApplication.job.jobAccessPermission.all():
                        # Step 2 Send individual notification
                        description = "Hello, We are pleased to inform you that you matched with one of your selected candidates: http://" + str(current_site.domain) + "/jobApplicationDetails/" + str(match.jobApplication.pk)
                        notify.send(request.user, recipient=employer.user, verb='Job Match: ' + match.candidate.user.preferredName + " " + match.candidate.user.firstName + " " + match.candidate.user.lastName, description = description, public=False)
                        if employer.notify_by_email:
                            email_to.add(employer.user.email)
                    email_to = list(email_to)
                    # Step 3: Create email for employer(s)
                    mail_subject = 'Concordia ACE Job Match: ' + match.candidate.user.preferredName + " " + match.candidate.user.firstName + " " + match.candidate.user.lastName
                    message = render_to_string('email-match-employer.html', {
                        'candidate': match.candidate,
                        'domain': current_site.domain,
                        'job': match.jobApplication.job,
                    })
                    email = EmailMessage(
                                mail_subject, message, to=email_to
                    )
                    if len(email_to) != 0:
                        messages.append(email)

                    # Step 4: Notify candiddate

                    candidate = match.candidate

                    description = "Congratulation! We have shared your contact information with your future employer."

                    notify.send(request.user, recipient=candidate.user, verb='Job Match: ' + match.jobApplication.job.title + " at " + match.jobApplication.job.company.name, description = description, public=False)
                    
                    # Step 5: Create email for the candidate
                    if candidate.notify_by_email:
                        mail_subject = 'Concordia ACE Job Match: ' + match.jobApplication.job.title + " at " + match.jobApplication.job.company.name
                        message = render_to_string('email-match-candidate.html', {
                            'user': match.candidate,
                            'domain': current_site.domain,
                            'job': match.jobApplication.job,
                        })
                        email = EmailMessage(
                                    mail_subject, message, to=[candidate.user.email]
                        )

                        messages.append(email)

                    match.isOpenToPublic = True
                    match.save()
                    
                # Final Step: Send messages
                
                try:
                    connection.send_messages(messages)
                except Exception as e:
                    import sys
                    print(e, file=sys.stderr)
                
                connection.close()
                context["message"] = "4 - Success. Matches are now visible to candidates and employers. Notifications and mass emails sent."

                    


            if request.POST.get("Undo last 7 days"):
                for rank in Ranking.objects.filter(updated_at__gte=timezone.now()-timedelta(days=7)).all():
                    rank.is_ranking_open_for_employer = True
                    rank.is_ranking_open_for_candidate = False
                    rank.is_closed = False
                    matchCount = Match.objects.filter(jobApplication=rank.jobApplication).count()
                    rank.jobApplication.job.vacancy += matchCount
                    rank.jobApplication.job.filled -= matchCount
                    rank.jobApplication.status = "Interviewing"
                    rank.status = "Interviewing"
                    rank.jobApplication.save()
                    rank.jobApplication.job.save()
                    rank.save()
                    for match in Match.objects.filter(jobApplication=rank.jobApplication):
                        match.delete()
                context["message"] = "Success. Reverted back to step 1 while preserving existing rankings"

        context["user"] = request.user
        
        context["newMessageCount"] = len(request.user.notifications.unread())
        context["announcements"] = RankingMessage.objects.filter().all()
        return render(request, "dashboard-ranking-matchday.html", context)

def admin_open_matching(request):
    if request.user.user_type == USER_TYPE_SUPER:
        return HttpResponseRedirect('/')

def view_matching(request, jobId= None):
    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login first"
        return HttpResponseRedirect('/login')


    if request.user.user_type == USER_TYPE_SUPER:

        if jobId == None:
        
            jobQuery = Job.objects.all()

            jobs = []


            for job in jobQuery:
                obj = {}

                obj['job'] = job
                obj['count'] = Match.objects.filter(job=job).count()
                jobs.append(obj)

            context = {
                        "jobs" : jobs,
                        'user' : request.user,
                    }

        else:
            jobQuery = get_object_or_404(Job, id=jobId)

            context = {
                        "job" : jobQuery,
                        }


            matches = Match.objects.filter(job__id=jobId)

            context["matches"] = matches

    if request.user.user_type == USER_TYPE_EMPLOYER:

        if jobId == None:
            jobQuery = Job.objects.filter(jobAccessPermission = Employer.objects.get(user=request.user))


            jobs = []
            for job in jobQuery:
                obj = {}
                obj['job'] = job
                obj['count'] = Match.objects.filter(job=job, isOpenToPublic=True).count()
                jobs.append(obj)

            context = {
                        "jobs" : jobs,
                        'user' : request.user,
                        }
        else:
            jobQuery = get_object_or_404(Job, id=jobId, jobAccessPermission = Employer.objects.get(user=request.user))


            context = {
                        "job" : jobQuery,
                        }

            matches = Match.objects.filter(job__id=jobId, isOpenToPublic=True)

            context["matches"] = matches


    if request.user.user_type == USER_TYPE_CANDIDATE:

        matches = Match.objects.filter(candidate=Candidate.objects.get(user=request.user), isOpenToPublic=True)

        context = {
                    "job": True,
                    "matches" : matches,
                    }       
    context["newMessageCount"] = len(request.user.notifications.unread())
    context["announcements"] = MatchingMessage.objects.filter().all()
    return render(request, "dashboard-match.html", context)