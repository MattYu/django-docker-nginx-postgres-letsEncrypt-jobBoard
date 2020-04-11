from django.shortcuts import render
from accounts.forms import RegistrationForm, LoginForm
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from accounts.models import account_activation_token, User
from django.core.mail import EmailMessage
from django.db import transaction 
from django.http import HttpResponse

from .decorators import check_recaptcha

DEBUG =True

# Create your views here.
@check_recaptcha
def register_user(request):
    context = {}
    
    if (request.method == 'POST'):
        form = RegistrationForm(
            request.POST, 
            request.FILES,
            registrationType=request.POST.get('registrationType'),
            employerCompany=request.POST.get('employerCompany'),
            extra_language_count=request.POST.get('extra_language_count'),
            )
        print(form.errors)
        if form.is_valid() and request.recaptcha_is_valid:
            
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=raw_password)
            login(request, user)

            current_site = get_current_site(request)
            mail_subject = 'Activate your Concordia ACE account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )

            try:
                email.send()
                messages.success(request, 'Candidate account created!')
            except:
                pass
            return HttpResponseRedirect('/')


    else:
        form = RegistrationForm(registrationType=None, employerCompany=None, extra_language_count=1)

    if request.user.is_authenticated:
        return render(request, "404.html")
    context['form'] = form

    return render(request, "register.html", context)

@transaction.atomic
def login_user(request):
    if (request.method == 'POST'):
        form = LoginForm(request.POST)

        if form.is_valid():

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
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')