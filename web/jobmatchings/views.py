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

    return render(request, "dashboard-ranking-candidate.html", context)

@transaction.atomic
def admin_matchmaking(request):
    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login first"
        return HttpResponseRedirect('/login')


    if request.user.user_type == USER_TYPE_SUPER:

        if (request.method == "POST"):

            if request.POST.get("closeEmp"):

                for rank in Ranking.objects.filter(is_ranking_open_for_employer=True):
                    rank.is_ranking_open_for_employer = False
                    rank.is_ranking_open_for_candidate = True
                    rank.save()

            if request.POST.get("closeCan"):
                for rank in Ranking.objects.filter(is_ranking_open_for_candidate=True):
                    rank.is_ranking_open_for_candidate = False
                    rank.save()

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

                for rank in Ranking.objects.filter(~Q(status="Not Matched")).order_by('employerRank'):
                    jobId = rank.jobApplication.job.id
                    job = rank.jobApplication.job

                    if jobId not in employer_prefs:
                        employer_prefs[jobId] = [rank.candidate.id]
                        capacities[jobId] = job.vacancy
                        print(capacities[jobId])
                    else:
                        employer_prefs[jobId].append(rank.candidate.id)
                
                candidate_prefs = {}
                for rank in Ranking.objects.filter(~Q(status="Matched") | ~Q(status="Not Matched")).order_by('candidateRank'):
                    candidate = rank.candidate.id

                    if candidate not in candidate_prefs:
                        candidate_prefs[candidate] = [rank.jobApplication.job.id]
                    else:
                        candidate_prefs[candidate].append(rank.jobApplication.job.id)

                match = ranking.HospitalResident.create_from_dictionaries( candidate_prefs, employer_prefs, capacities)

                matchResult = match.solve(optimal="resident")
                print(matchResult)

                for j in matchResult:
                    print(j)

                for jobObj in matchResult:
                    print("test job")
                    print(jobObj)
                    for candidate in matchResult[jobObj]:
                        print("test candidate")
                        print(candidate)
                        match = Match()
                        # Before creating a match, perform a safety check to see if candidate already have been matched by the same employer for the same job before
                        if Match.objects.filter(candidate=Candidate.objects.get(id=int(candidate.name)), job= Job.objects.get(id=int(jobObj.name))).count() == 0:
                            match.candidate = Candidate.objects.get(id=int(candidate.name))
                            job = Job.objects.get(id=int(jobObj.name))
                            match.job = job
                            match.jobApplication = JobApplication.objects.filter(candidate=Candidate.objects.get(id=int(candidate.name)), job= job).first()
                            match.save()
                            #match.jobApplication.status = "Matched"
                            match.jobApplication.save()

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

            if request.POST.get("open"):
                for rank in Ranking.objects.filter(is_closed=False):
                    if Match.objects.filter(jobApplication=rank.jobApplication).count() == 0:
                        print(rank.jobApplication.status)
                        rank.jobApplication.status = "Not Matched"
                        print(rank.jobApplication)
                        rank.is_closed = True
                        rank.save()
                        rank.jobApplication.save()
                    else:
                        print(rank.jobApplication.status)
                        rank.jobApplication.status = "Matched"
                        rank.is_closed = True
                        rank.save()
                        rank.jobApplication.save()
                for match in Match.objects.filter(isOpenToPublic=False):
                        match.isOpenToPublic = True
                        match.save()

            if request.POST.get("Undo last 7 days"):
                print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT1111111111111111111111")
                for rank in Ranking.objects.filter():
                    print(rank.updated_at)
                for rank in Ranking.objects.filter(updated_at__gte=timezone.now()-timedelta(days=7)).all():
                    print("isThisWorking")
                    rank.is_ranking_open_for_employer = True
                    rank.is_ranking_open_for_candidate = False
                    rank.is_closed = False
                    matchCount = Match.objects.filter(jobApplication=rank.jobApplication).count()
                    print(matchCount)
                    print(rank.jobApplication.job.vacancy)
                    print(rank.jobApplication.job.filled)
                    rank.jobApplication.job.vacancy += matchCount
                    rank.jobApplication.job.filled -= matchCount
                    rank.jobApplication.status = "Interviewing"
                    rank.status = "Interviewing"
                    rank.jobApplication.save()
                    rank.jobApplication.job.save()
                    print("test")
                    print(rank.jobApplication.job.vacancy)
                    print(rank.jobApplication.job.filled)
                    rank.save()
                    for match in Match.objects.filter(jobApplication=rank.jobApplication):
                        match.delete()

        context = {
            "user": request.user
            }

    return render(request, "dashboard-ranking-matchday.html", context)



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

    return render(request, "dashboard-match.html", context)