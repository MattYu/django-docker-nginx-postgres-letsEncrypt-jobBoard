from django.shortcuts import render, get_object_or_404
from accounts.forms import RegistrationForm, LoginForm, CandidateEditProfileForm
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.db.models import Q
from accounts.models import Employer
from joblistings.models import Job

from ace.constants import USER_TYPE_SUPER, RECAPTCHA_PUBLIC_KEY, USER_TYPE_CANDIDATE, USER_TYPE_EMPLOYER, MAX_PER_PAGE
from accounts.models import Candidate, Language

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from accounts.models import account_activation_token, User, concordia_email_confirmation_token
from django.core.mail import EmailMessage
from django.db import transaction 
from django.http import HttpResponse

from jobapplications.models import JobApplication

from .decorators import check_recaptcha
from notifications.signals import notify
import ace.settings as settings
import json
import urllib
import requests as requests
import ace.settings as settings

from jobapplications.forms import FilterApplicationForm
from django.db.models import Q
import re
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import json as simplejson

DEBUG =True

# Create your views here.
@check_recaptcha
@transaction.atomic
def register_user(request, employer=None):
    context = {}
    
    if (request.method == 'POST'):
        form = RegistrationForm(
            request.POST, 
            request.FILES,
            registrationType=request.POST.get('registrationType'),
            employerCompany=request.POST.get('employerCompany'),
            extra_language_count=request.POST.get('extra_language_count'),
            )
        
        if 'Register' in request.POST and request.recaptcha_is_valid:
            context["showError"] = True
            #if form.is_valid() and request.recaptcha_is_valid:
            if form.is_valid():
                form.save(request)
                email = form.cleaned_data.get('email')
                raw_password = form.cleaned_data.get('password')
                user = authenticate(email=email, password=raw_password)
                login(request, user)
                messages.success(request, 'Candidate account created!')

                return HttpResponseRedirect('/activate')

    else:
        if employer and employer==1:
            form = RegistrationForm(registrationType="employer", employerCompany=None, extra_language_count=1)
        elif employer and employer==2:
            form = RegistrationForm(registrationType=None, employerCompany="candidate", extra_language_count=1)
        else:
            form = RegistrationForm(registrationType=None, employerCompany=None, extra_language_count=1)

    if request.user.is_authenticated:
        return render(request, "404.html")

    context['form'] = form
    context['recaptchaPubKey'] = RECAPTCHA_PUBLIC_KEY

    return render(request, "register.html", context)

@check_recaptcha
@transaction.atomic
def login_user(request):
    context = {}
    if (request.method == 'POST'):
        form = LoginForm(request.POST)
        #if form.is_valid() and request.recaptcha_is_valid:
        import sys
        print(request.recaptcha_is_valid, file=sys.stderr)
        
        if form.is_valid() and request.recaptcha_is_valid:

            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=raw_password)

            if not user:
                request.session['warning'] = "Wrong email or password entered"
                context = {'form': form}
                return  HttpResponseRedirect('/login')

            login(request, user)


            if 'redirect' in request.session:
                redirect = request.session['redirect']
                del request.session['redirect']
                return HttpResponseRedirect(redirect)
            if not request.user.is_email_confirmed:
                return HttpResponseRedirect('/activate')
            return HttpResponseRedirect('/')
        else:
            context['form'] = form
            context['recaptchaPubKey'] = RECAPTCHA_PUBLIC_KEY
            return render(request, "login.html", context)

    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    form = LoginForm()
    context = {'form': form}

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

    if 'attempts' in request.session:
        request.session['attempts'] += 1
        if request.session['attempts'] > 3:
            context['locked'] = True
    else:
        request.session['attempts'] = 1
        context['locked'] = False
    context['recaptchaPubKey'] = RECAPTCHA_PUBLIC_KEY
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')
    
@transaction.atomic
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_email_confirmed = True
        user.save()
        return HttpResponseRedirect('/validated')
        # return redirect('home')
        #return HttpResponse('Thank you for your email confirmation. Now you can log into your account.')
    else:
        return render(request, "activationLink.html", context={'message':'Activation link is invalid!'})

@transaction.atomic
def validate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and concordia_email_confirmation_token.check_token(user, token):
        try:
            candidate = Candidate.objects.get(user=user)
            candidate.is_concordia_email_confirmed = True
            candidate.save()
            # return redirect('home')
            return render(request, "activationLink.html", context={'message':'Thank you for your secondary email confirmation.'})
        except Exception as e:
            return render(request, "activationLink.html", context={'message':"Confirmation link is invalid!"})
    else:
        return render(request, "activationLink.html", context={'message':'Confirmation link is invalid!'})

def resend_activation(request):
    if request.user.is_authenticated:
        user =request.user
        email = user.email
        current_site = get_current_site(request)
        mail_subject = 'Activate your Concordia ACE account.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        to_email = email
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )

        try:
            email.send()
            description = "We have sent you another confirmation link to " + to_email + ". If you have not received the link, please click here "
        except Exception as e:
            import sys
            print(e, file=sys.stderr)

        return render(request, "activationLink.html", context = {'message': 'An activation link has been sent to your account. Please check your spam folder first.', 'resend': True})

    else:
        return HttpResponse('You must be logged in to resend your email activation link')

def manage_employers(request, searchString=""):
    if request.user.is_authenticated and request.user.user_type == USER_TYPE_SUPER:

        orderby = '-created_at'

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
        if "alphabeticalFirstName" in search:
            orderby = '-user__firstName'
        if "alphabeticalLastName" in search:
            orderby = '-user__lastName'
        
        if (request.method == 'POST'):
            if "Approved" in  request.POST:
                employer = get_object_or_404(Employer, pk = int(request.POST.get("Approved")))
                employer.status = "Approved"
                employer.approved = True
                employer.save()
            if "Not Approved" in  request.POST:
                employer = get_object_or_404(Employer, pk = int(request.POST.get("Not Approved")))
                employer.status = "Not Approved"
                employer.approved = False
                employer.save()

                allJobs = Job.objects.all()
                if allJobs:
                    for job in allJobs:
                        if employer in job.jobAccessPermission.all():
                            job.jobAccessPermission.remove(employer)
                            job.save()

        filterquery = Q()
        employers = Employer.objects.filter(filterquery).order_by(orderby).all()
        
        context = {
            "employers": employers,
        }
        context["newMessageCount"] = len(request.user.notifications.unread())
        return render(request, "dashboard-manage-employer.html", context)

    else:
        return HttpResponse('Invalid permission')

def activate_account(request):
    context = {}

    if request.user.is_authenticated and not request.user.is_email_confirmed:
        return render(request, "activate-account.html", context)
    if request.user.is_email_confirmed:
        return render('Your email address has already been validated')

def validated(request):

    return render(request, "validated.html")


def edit_profile(request):
    if request.user.is_authenticated and request.user.user_type == USER_TYPE_CANDIDATE:
        candidate = get_object_or_404(Candidate, user = request.user)
        context = {'candidate' : candidate}
        languages = Language.objects.filter(user=request.user)
        context['subject'] = candidate
        context['languages'] = languages
        context["newMessageCount"] = len(request.user.notifications.unread())
        return render(request, 'edit-profile.html', context)
    
    if request.user.is_authenticated and request.user.user_type == USER_TYPE_EMPLOYER:
        employer = get_object_or_404(Employer, user = request.user)
        context = {'employer' : employer}
        context["newMessageCount"] = len(request.user.notifications.unread())
        return render(request, 'edit-profile.html', context)

    if request.user.is_authenticated and request.user.user_type == USER_TYPE_SUPER:

        return HttpResponseRedirect('/admin/accounts/user/' + str(request.user.pk) + "/change")

    return HttpResponse('403 Permission Denied')


@transaction.atomic
def edit_candidate_profile(request, employer=None):
    context = {}
    
    if not request.user.is_authenticated:
        return render(request, "404.html")
    
    if request.user.user_type != USER_TYPE_CANDIDATE:
        return render(request, "404.html")

    if (request.method == 'POST'):
        form = CandidateEditProfileForm(
            request.POST, 
            request.FILES,
            extra_language_count=request.POST.get('extra_language_count'),
            )

        
        if 'Update' in request.POST:
            context["showError"] = True
            #if form.is_valid() and request.recaptcha_is_valid:
            if form.is_valid():
                form.save(request)
                return HttpResponseRedirect('/edit-profile')
    else:
        form = CandidateEditProfileForm(extra_language_count=1)


    context['form'] = form

    return render(request, "edit-profile-candidate.html", context)

@transaction.atomic
def browse_candidate(request, searchString = ""):
    context = {}
    candidates = None
    form = FilterApplicationForm()
    query = Q()
    page = 1

    filterClasses = []
    filterHTML = []
    sortOrder = '-created_at'

    if not request.user.is_authenticated:

        request.session['redirect'] = request.path
        request.session['warning'] = "Warning: Please login before applying to a job"
        return HttpResponseRedirect('/login')
        
    if request.user.user_type != USER_TYPE_SUPER:
        return HttpResponseRedirect('/')


    if (request.method == 'POST'):
        form = FilterApplicationForm(request.POST, page=request.POST.get('page'),)        
        page = int(form.fields['page'].initial)
        if 'filter' in request.POST or 'nextPage' in request.POST or 'prevPage' in request.POST:
            context['filterClasses'] = simplejson.dumps(form.getSelectedFilterClassAsList())
            context['filterHTML'] = simplejson.dumps(form.getSelectedFilterHTMLAsList())
            #for ob in request.POST.get('selected_filter'):
            #    print(ob)
            #print("test***")

    # Applying filter value here
    filterSet = form.getSelectedFilterAsSet()
    newSet = set()
    for element in filterSet:
        newSet.add(re.sub('[^A-Za-z0-9 ]', '', element))
    filterSet = newSet
    import sys
    #print(filterSet, file=sys.stderr)
    try:
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
        if request.user.user_type != USER_TYPE_CANDIDATE:
            if form["firstName"].value() != None and form["firstName"].value() != "":
                query &= (Q(user__firstName__icontains= form["firstName"].value()) | Q(user__preferredName__contains=form["firstName"].value()))
            if form["lastName"].value() != None and form["lastName"].value() != "":
                query &= Q(user__lastName__icontains= form["lastName"].value())
            if form["email"].value() != None and form["email"].value() != "":
                query &= (Q(user__email__icontains=form["email"].value()) | Q(concordia_email__icontains=form["email"].value()))
            if form["studentId"].value() != None and form["studentId"].value() != "":
                query &= Q(studentID__icontains=form["studentId"].value())
            try:
                if form["gpa_min"].value() != None and form["gpa_min"].value() != "1.7" :
                    query &= Q(gpa__gte = float(form["gpa_min"].value()))
                
                if form["gpa_max"].value() != None and form["gpa_max"].value() != "4.3" :
                    query &= Q(gpa__lte = float(form["gpa_max"].value()))
            except:
                pass
        if form["program"].value() != None and form["program"].value() != "ANY":
            query &= Q(program= form["program"].value())
        if 'Oldest First' in filterSet:
            sortOrder = 'created_at'
        if "Canadian" in filterSet:
            query &= Q(citizenship="Canadian")
        if "Permanent Resident" in filterSet:
            query &= Q(citizenship="Permanent Resient")
        if "International Student" in filterSet:
            query &= Q(citizenship="International Student")
        if "Concordia Student confirmed email" in filterSet:
            query &= Q(is_concordia_email_confirmed=True)
    except Exception as e:
        import sys
        print(e, file=sys.stderr)
    if 'oldest' in searchString:
        sortOrder = 'created_at'


    candidatesList = Candidate.objects.filter(query).order_by(sortOrder)
    context["candidatesList"] = candidatesList
    context["form"] = form
    #import sys
    #print(query, file=sys.stderr)
    
    if (request.method == 'POST'):
        
        if 'contact' in request.POST:
            emails = set()
            emails_do_not_disturbe = set()
            candidates = {}

            for candidate in candidatesList:
                if candidate.notify_by_email:
                    emails.add(candidate.user.email)
                else:
                    emails_do_not_disturbe.add(candidate.user.email)
                applications  = JobApplication.objects.filter(candidate=candidate).all()
                candidates[candidate] = []
                for application in applications:
                    candidates[candidate].append(application)

            context["emails"] = emails
            context["emails_do_not_disturbe"] = emails_do_not_disturbe
            context["candidates"] = candidates
            return render(request, "contact_info.html", context)

    context["newMessageCount"] = len(request.user.notifications.unread())


    #form.fields['page'].initial = 4
    #print(form.fields['page'].initial)

    maxCount = len(context['candidatesList'])

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
   
    context['candidatesList'] = context['candidatesList'][low:high]

    if page == 1:
        context['hideLow'] = True
    if page == maxPage:
        context['hideHigh'] = True

    return render(request, "dashboard-manage-candidates.html", context)