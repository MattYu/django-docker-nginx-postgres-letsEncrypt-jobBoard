from django.shortcuts import render, get_object_or_404
from accounts.forms import RegistrationForm, LoginForm
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.db.models import Q
from accounts.models import Employer
from joblistings.models import Job

from ace.constants import USER_TYPE_SUPER, RECAPTCHA_PUBLIC_KEY
from accounts.models import Candidate

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

from .decorators import check_recaptcha
from notifications.signals import notify
import ace.settings as settings
import json
import urllib
import requests as requests
import ace.settings as settings

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

        if settings.DEV == True:
            request.recaptcha_is_valid = True
        
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
    if (request.method == 'POST'):
        form = LoginForm(request.POST)
        #if form.is_valid() and request.recaptcha_is_valid:
        import sys
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        ''' Begin reCAPTCHA validation '''
        recaptcha_response = request.POST.get('g-recaptcha-response')
        print(recaptcha_response, file=sys.stderr)
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req =  urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        ''' End reCAPTCHA validation '''

        if settings.DEV == True:
            result['success'] = True
        
        if form.is_valid() and result['success']:

            email = form.cleaned_data.get('email')
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

    if request.user.is_authenticated:
        return render(request, "404.html")

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
        return HttpResponse('Activation link is invalid!')

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
            return HttpResponse('Thank you for your secondary email confirmation.')
        except Exception as e:
            return HttpResponse("Confirmation link is invalid!")
    else:
        return HttpResponse('Confirmation link is invalid!')

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
            description = "We have sent you another confirmation link to " + email + ". If you have not received the link, please click here "
        except Exception as e:
            import sys
            print(e, file=sys.stderr)

        return HttpResponse('A new activation link has been sent to your email account.')

    else:
        return HttpResponse('You must be logged in to resend your email activation link')

def manage_employers(request, searchString=""):
    if request.user.is_authenticated and request.user.user_type == USER_TYPE_SUPER:
        
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
        employers = Employer.objects.filter(filterquery).order_by('-created_at').all()
        
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
        return HttpResponse('Your email address has already been validated')

def validated(request):

    return render(request, "validated.html")