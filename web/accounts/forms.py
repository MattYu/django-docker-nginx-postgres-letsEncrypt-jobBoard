from django import forms
from ace.constants import AGREE_DISAGREE, PASSWORD_MIN_LENGTH, MAX_LENGTH_STANDARDFIELDS, MAX_LENGTH_LONGSTANDARDFIELDS, USER_TYPE_CANDIDATE, USER_TYPE_EMPLOYER, LANGUAGE_CHOICES, LANGUAGE_FLUENCY_CHOICES, YES_NO, CITIZENSHIP, CATEGORY_CHOICES
from accounts.models import Candidate, Employer, PreferredName, MyUserManager
from accounts.models import User, Language
from companies.models import Company
from tinymce.widgets import TinyMCE
from django.shortcuts import get_object_or_404
import re

from notifications.signals import notify
from accounts.models import account_activation_token, User, concordia_email_confirmation_token
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.core import mail
from ace.models import Employer_termsAndConditions, Candidate_termsAndConditions

class RegistrationForm(forms.Form):
    registrationType = forms.CharField(widget=forms.HiddenInput(), required=False)
    employerCompany = forms.CharField(widget=forms.HiddenInput(), required=False)
    extra_language_count = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    email = forms.EmailField(max_length=MAX_LENGTH_STANDARDFIELDS,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
                                )

    password = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    passwordConfirm = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))

    firstName = forms.CharField(max_length=MAX_LENGTH_STANDARDFIELDS,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
                                )

    lastName = forms.CharField(max_length=MAX_LENGTH_STANDARDFIELDS,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
                                )
    
    preferredName = forms.CharField(required=False, max_length=MAX_LENGTH_STANDARDFIELDS,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preferred First Name (optional)'})
                                )

    phoneNumber = forms.CharField(max_length=MAX_LENGTH_STANDARDFIELDS,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'})
                            )


    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        registrationType = kwargs.pop('registrationType', None)
        companyType = kwargs.pop('employerCompany', None)
        extra_language_fields = kwargs.pop('extra_language_count', 1)
        super().__init__(*args, **kwargs)
        self.fields['extra_language_count'].initial = max(min(int(extra_language_fields), 10),1)
        self.fields['registrationType'].initial =registrationType
        self.fields['employerCompany'].initial =companyType
        self.languageFields = []
        self.languageFieldsNames = []
        self.raise_errors = []
        self.termsAndConditionsFields = []
        self.termsAndConditionsFieldsNames = []

        if (registrationType == "employer"):
            if (companyType == 'createNew'):
                self.fields['companyName'] = forms.CharField(max_length = 100,  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}))
                self.fields['address'] = forms.CharField(max_length = 100,  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company address'}))
                self.fields['website'] = forms.CharField(max_length = 100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company website'}))
                self.fields['image'] =   forms.ImageField(required=False)

                try:
                    employer_termsAndConditions = Employer_termsAndConditions.objects.all()
                except:
                    employer_termsAndConditions = []

                self.employer_termsAndConditions = employer_termsAndConditions

                for i in range(len(employer_termsAndConditions)):
                    self.add_termsAndConditions(employer_termsAndConditions[i], i)

            if (companyType == 'selectFromExisting'):
                self.fields['company'] = forms.ChoiceField(
                                                            widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Category'})
                                                        )
                company = Company.objects.filter(is_approved=True).order_by('-name').all()
                company_choices = []
                for obj in company:
                    company_choices.append((obj.pk, obj))
                self.fields['company'].choices = company_choices
                try:
                    employer_termsAndConditions = Employer_termsAndConditions.objects.all()
                except:
                    employer_termsAndConditions = []

                self.employer_termsAndConditions = employer_termsAndConditions

                for i in range(len(employer_termsAndConditions)):
                    self.add_termsAndConditions(employer_termsAndConditions[i], i)

        if (registrationType == "candidate"):
                self.fields['studentID'] = forms.CharField(max_length=MAX_LENGTH_STANDARDFIELDS,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student ID'})
                                        )
                self.fields['creditCompleted'] = forms.FloatField(
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Credits Completed'})
                                        )
                self.fields['creditLeft'] = forms.FloatField(
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Credits left'})
                                        )
                
                self.fields['gpa'] = forms.FloatField(
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cumulative GPA'})
                                        )

                self.fields['concordia_email'] = forms.EmailField(max_length=MAX_LENGTH_STANDARDFIELDS,
                                                                    required=False,
                                                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Concordia Email (Optional)'})
                                                                    )
                for i in range(int(self.fields['extra_language_count'].initial)):
                    self.add_language(i)

                self.fields['program'] = forms.ChoiceField(
                                                                    choices=CATEGORY_CHOICES,
                                                                    widget=forms.Select(attrs={'class': 'form-control'})
                                                                )

                self.fields['citizenship'] = forms.ChoiceField(
                                                                    choices=CITIZENSHIP,
                                                                    widget=forms.Select(attrs={'class': 'form-control'})
                                                                )
                

                self.fields['transcript'] =   forms.FileField(required=False)

                try:
                    candidate_termsAndConditions = Candidate_termsAndConditions.objects.all()
                except Exception as e:
                    candidate_termsAndConditions = []
                    import sys
                    print(e, file=sys.stderr)
                self.candidate_termsAndConditions = Candidate_termsAndConditions

                for i in range(len(candidate_termsAndConditions)):
                    self.add_termsAndConditions(candidate_termsAndConditions[i], i)


    def add_language(self, i:int = None):
        if i == None:
            i = len(self.languageFields)
        field_name = '_language_%s' % (i,)
        languageDict = {}
        lanNameDict = {}

        self.fields['language' + field_name] = forms.ChoiceField(
                                                                    choices=LANGUAGE_CHOICES,
                                                                    widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Language'})
                                                                )
        languageDict['language'] = self['language' + field_name]
        lanNameDict['language'] = 'language' + field_name
        self.fields['proficiency' + field_name] = forms.ChoiceField(
                                                                    choices=LANGUAGE_FLUENCY_CHOICES,
                                                                    widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Proficiency'})
                                                                )
        languageDict['proficiency'] = self['proficiency' + field_name]
        lanNameDict['proficiency'] = 'proficiency' + field_name
        self.fields['details' + field_name] = forms.CharField(      
                                                                    required= False,
                                                                    max_length=25,
                                                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Details (optional)'})
                                                            )
        languageDict['details'] = self['details' + field_name]
        lanNameDict['details'] = 'details' + field_name
        
        self.languageFields.append(languageDict)
        self.languageFieldsNames.append(lanNameDict)

        return languageDict

    def add_termsAndConditions(self, termsAndConditions, i:int = None):
        field_name = '_tAndC_%s' % (i,)
        tAndDDict = {}
        tAndDNameDict = {}

        self.fields['radio' + field_name] = forms.ChoiceField(choices=AGREE_DISAGREE, widget=forms.RadioSelect)
        tAndDDict['radio'] = self['radio' + field_name]
        tAndDNameDict['radio'] = 'radio' + field_name

        tAndDDict['obj'] = termsAndConditions
        tAndDNameDict['obj'] = 'obj' + field_name
        
        self.termsAndConditionsFields.append(tAndDDict)
        self.termsAndConditionsFieldsNames.append(tAndDNameDict)

        return tAndDDict

                
    def get_language_fields(self):
        return self.languageFields

    def get_terms_and_conditions(self):
        return self.termsAndConditionsFields

    def check_max_language_count(self):
        return len(self.languageFields) >= 10


    def is_type_selected(self)-> bool:
        if self.fields['registrationType'].initial == 'employer' or self.fields['registrationType'].initial == 'candidate':
            return True
        return False

    def is_employer_selected(self)-> bool:
        if self.fields['registrationType'].initial == 'employer':
            return True
        return False

    def is_candidate_selected(self)-> bool:
        if self.fields['registrationType'].initial == 'candidate':
            return True
        return False
    
    def is_createCompany_selected(self)-> bool:
        if self.fields['employerCompany'].initial == 'createNew':
            return True
        return False
        

    def isAllFieldSelected(self)-> bool:
        if self.fields['registrationType'].initial != 'employer' and self.fields['registrationType'].initial != 'candidate':
            return False
        if self.fields['registrationType'].initial == 'employer':
            if self.fields['employerCompany'].initial != 'selectFromExisting' and self.fields['employerCompany'].initial != 'createNew':
                return False
        return True

    def clean(self):
        self.raise_errors = []
        cleaned_data = super().clean()
        User.objects.all()

        if cleaned_data.get('email') != "" and self.is_valid():
                if not re.match(r"[^@]+@[^@]+\.[^@]+", str(cleaned_data.get('email'))): 
                    self.raise_errors.append('Invalid Email address')
        if cleaned_data.get('password') != cleaned_data.get('passwordConfirm'):
            #raise forms.ValidationError('Passwords do not match')
            self.raise_errors.append('Passwords do not match')
        if User.objects.filter(email=cleaned_data.get('email')).count() != 0:
            #raise forms.ValidationError('Email is already in use')
            self.raise_errors.append('Email is already in use')
        if self.is_createCompany_selected() and self.is_createCompany_selected():
            if not cleaned_data.get('image') and self.is_valid():
                #raise forms.ValidationError('You have to upload a logo for your company')
                self.raise_errors.append('You have to upload a logo for your company')
            if cleaned_data.get('image') and not str(cleaned_data.get('image').name).lower().endswith(".png"):
                if not str(cleaned_data.get('image').name).lower().endswith(".jpg"):
                    self.raise_errors.append('Your company logo must be a .png or .jpg file')
        if self.is_candidate_selected():
            if not cleaned_data.get('transcript') and self.is_valid():
                #raise forms.ValidationError('You have to upload a transcript')
                self.raise_errors.append('You have to upload a transcript')
            if cleaned_data.get('transcript') and not cleaned_data.get('transcript').name.lower().endswith(".pdf"):
                self.raise_errors.append('Transcript must be in pdf format')

            if cleaned_data.get('concordia_email') != "":
                if not re.match(r"[^@]+@[^@]+\.[^@]+", str(cleaned_data.get('concordia_email'))): 
                    #raise forms.ValidationError("Invalid Concorda Email address")
                    self.raise_errors.append('Invalid Concorda Email address')

            if (cleaned_data.get('program') == "Any Category" or cleaned_data.get('program') == "ANY") and self.is_valid():
                    self.raise_errors.append('Please specify your program of study')
            if cleaned_data.get('citizenship') == "Choose" and self.is_valid():
                    self.raise_errors.append('Please specify your citizenship status')

        password = self.cleaned_data.get('password')

        if password != None:
            if len(password) < PASSWORD_MIN_LENGTH:
                #raise forms.ValidationError("The new password must be at least %d characters long." % PASSWORD_MIN_LENGTH)

                self.raise_errors.append("The password must be at least %d characters long." % PASSWORD_MIN_LENGTH)
            # At least one letter and one non-letter
            first_isalpha = password[0].isalpha()
            if all(c.isalpha() == first_isalpha for c in password):
                #raise forms.ValidationError("The new password must contain at least one letter and at least one digit or" " punctuation character.")

                self.raise_errors.append("The password must contain at least one letter and at least one digit or punctuation character.")

        if self.raise_errors:
            raise forms.ValidationError(self.raise_errors)
        
        self.cleaned_data = cleaned_data

    def save(self, request):
        self.clean()
        cleaned_data = self.cleaned_data
        userManager = MyUserManager()
        email = cleaned_data.get('email')
        firstName = cleaned_data.get('firstName')
        lastName = cleaned_data.get('lastName')
        phoneNumber = cleaned_data.get('phoneNumber')
        user_type = None
        if self.is_employer_selected():
            user_type = USER_TYPE_EMPLOYER
        else:
            user_type = USER_TYPE_CANDIDATE
        password = cleaned_data.get('password')
        
        user = User()
        user.email = email
        user.firstName = firstName
        user.lastName = lastName
        user.phoneNumber = phoneNumber
        user.user_type = user_type


        user.set_password(password)
        user.save()
        
        if cleaned_data.get('preferredName') != '' and cleaned_data.get('preferredName') !=None:
            user.preferredName = cleaned_data.get('preferredName')
            user.save()

        if self.is_employer_selected():
            employer = Employer()
            employer.user = user

            if self.is_createCompany_selected():
                company = Company()
                company.name = cleaned_data.get('companyName')
                company.address = cleaned_data.get('address')
                company.website = cleaned_data.get('website')
                company.image = cleaned_data.get('image')
                company.save()
                employer.company = company

            else:
                employer.company = get_object_or_404(Company, pk=cleaned_data.get('company'))

            employer.save()

            try:
                employer_termsAndConditions = Employer_termsAndConditions.objects.all()
            except:
                employer_termsAndConditions = []

            for condition in employer_termsAndConditions:
                condition.agreedList.add(employer)
                condition.save()
        else:
            candidate = Candidate()
            candidate.user =user
            candidate.studentID = cleaned_data.get('studentID')
            candidate.creditCompleted = cleaned_data.get('creditCompleted')
            candidate.program = cleaned_data.get('program')
            candidate.creditLeft = cleaned_data.get('creditLeft')
            candidate.gpa = cleaned_data.get('gpa')
            candidate.citizenship = cleaned_data.get('citizenship')
            candidate.transcript = cleaned_data.get('transcript')
            if cleaned_data.get('concordia_email') != "":
                candidate.concordia_email = cleaned_data.get('concordia_email')
            candidate.save()

            try:
                candidate_termsAndConditions = Candidate_termsAndConditions.objects.all()
            except Exception as e:
                candidate_termsAndConditions = []

            for condition in candidate_termsAndConditions:
                condition.agreedList.add(candidate)
                condition.save()

            for lan in self.languageFieldsNames:
                language = Language()
                language.language = cleaned_data.get(lan['language'])
                language.fluency = cleaned_data.get(lan['proficiency'])
                language.details = cleaned_data.get(lan['details'])
                language.user = user
                language.save()

        messages = []
        email = cleaned_data.get('email')
        raw_password = cleaned_data.get('password')

        current_site = get_current_site(request)
        mail_subject = 'Activate your Concordia ACE account.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        to_email = self.cleaned_data.get('email')
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )

        try:
            email.send()
            description = "We have sent you a confirmation link to " + self.cleaned_data.get('email') + ". If you have not received the link, please click here " + "https://"+str(current_site.domain) + "/resend_activation"
            notify.send(user, recipient=user, verb='Welcome to ACE - Please confirm your email address', description = description, public=False)
        except Exception as e:
            import sys
            print(e, file=sys.stderr)
        
        if self.is_candidate_selected() and self.cleaned_data.get('concordia_email') != "":
            
            mail_subject = 'Confirm your Concordia email address for ACE'
            message = render_to_string('confirm_concordia_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':concordia_email_confirmation_token.make_token(user),
            })
            to_email = self.cleaned_data.get('concordia_email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )

            try:
                email.send()
                notify.send(user, recipient=user, verb='Confirmation link sent to ' + to_email, description = "Link not received? You may request a new one by going into your Dashboard->Edit Profile", public=False)
            except Exception as e:
                import sys
                print(e, file=sys.stderr)

        return user


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=MAX_LENGTH_STANDARDFIELDS,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
                            )

    password = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))