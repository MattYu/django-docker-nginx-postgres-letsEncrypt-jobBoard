from django import forms
from ace.constants import MAX_LENGTH_STANDARDFIELDS, MAX_LENGTH_LONGSTANDARDFIELDS, USER_TYPE_CANDIDATE, USER_TYPE_EMPLOYER, LANGUAGE_CHOICES, LANGUAGE_FLUENCY_CHOICES, YES_NO, CATEGORY_CHOICES
from accounts.models import Candidate, Employer, PreferredName, MyUserManager
from accounts.models import User, Language
from companies.models import Company
from tinymce.widgets import TinyMCE
from django.shortcuts import get_object_or_404

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

        if (registrationType == "employer"):
            if (companyType == 'createNew'):
                self.fields['companyName'] = forms.CharField(max_length = 100,  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}))
                self.fields['address'] = forms.CharField(max_length = 100,  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company address'}))
                self.fields['website'] = forms.CharField(max_length = 100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company website'}))
                self.fields['profile'] = forms.CharField(
                                                            max_length=1000,
                                                            widget=TinyMCE(attrs={'class': 'tinymce-editor tinymce-editor-2'})
                                                        )
                self.fields['image'] =   forms.ImageField(required=False)
            if (companyType == 'selectFromExisting'):
                self.fields['company'] = forms.ChoiceField(
                                                            widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Category'})
                                                        )
                company = Company.objects.all()
                company_choices = []
                for obj in company:
                    company_choices.append((obj.pk, obj))
                self.fields['company'].choices = company_choices

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
                for i in range(int(self.fields['extra_language_count'].initial)):
                    self.add_language(i)

                self.fields['program'] = forms.ChoiceField(
                                                                    choices=CATEGORY_CHOICES,
                                                                    widget=forms.Select(attrs={'class': 'form-control'})
                                                                )

                self.fields['internationalStudent'] = forms.ChoiceField(
                                                                    choices=YES_NO,
                                                                    widget=forms.Select(attrs={'class': 'form-control'})
                                                                )
                
                self.fields['travel'] = forms.ChoiceField(
                                                                    choices=YES_NO,
                                                                    widget=forms.Select(attrs={'class': 'form-control'})
                                                                )

                self.fields['timeCommitment'] = forms.ChoiceField(
                                                                    choices=YES_NO,
                                                                    widget=forms.Select(attrs={'class': 'form-control'})
                                                                )

                self.fields['transcript'] =   forms.FileField(required=False)


    def add_language(self, i:int = None):
        if i == None:
            i = len(self.languageFields)
        print(i)
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
                
    def get_language_fields(self):
        return self.languageFields

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
        cleaned_data = super().clean()
        User.objects.all()

        if cleaned_data.get('password') != cleaned_data.get('passwordConfirm'):
            raise forms.ValidationError('Passwords do not match')
        if User.objects.filter(email=cleaned_data.get('email')).count() != 0:
            raise forms.ValidationError('Email is already in use')

        if self.is_createCompany_selected() and self.is_createCompany_selected() and self.is_valid():
            if not cleaned_data.get('image'):
                raise forms.ValidationError('You have to upload a logo for your company')

        if self.is_candidate_selected() and self.is_valid():
            if not cleaned_data.get('transcript'):
                raise forms.ValidationError('You have to upload a transcript')

        self.cleaned_data = cleaned_data

    def save(self):
        self.clean()
        cleaned_data = self.cleaned_data
        userManager = MyUserManager()
        email = cleaned_data.get('email')
        firstName = cleaned_data.get('firstName')
        lastName = cleaned_data.get('lastName')
        user_type = None
        if self.is_employer_selected():
            user_type = USER_TYPE_EMPLOYER
        else:
            user_type = USER_TYPE_CANDIDATE
        password = cleaned_data.get('password')
        print(user_type)

        
        user = User()
        user.email = email
        user.firstName = firstName
        user.lastName = lastName
        user.user_type = user_type


        user.set_password(password)
        user.save()
        
        if cleaned_data.get('preferredName') != '' and cleaned_data.get('preferredName') !=None:
            preferredName = PreferredName()
            preferredName.user = user
            preferredName.preferredName = cleaned_data.get('preferredName')
            preferredName.save()

        if self.is_employer_selected():
            employer = Employer()
            employer.user = user

            if self.is_createCompany_selected():
                company = Company()
                company.name = cleaned_data.get('companyName')
                company.address = cleaned_data.get('address')
                company.website = cleaned_data.get('website')
                company.profile = cleaned_data.get('profile')
                company.image = cleaned_data.get('image')
                company.save()
                employer.company = company

            else:
                employer.company = get_object_or_404(Company, pk=cleaned_data.get('company'))

            employer.save()
        else:
            candidate = Candidate()
            candidate.user =user
            candidate.studentID = cleaned_data.get('studentID')
            candidate.creditCompleted = cleaned_data.get('creditCompleted')
            candidate.program = cleaned_data.get('program')
            candidate.creditLeft = cleaned_data.get('creditLeft')
            candidate.gpa = cleaned_data.get('gpa')
            candidate.internationalStudent = cleaned_data.get('internationalStudent')
            candidate.travel = cleaned_data.get('travel')
            candidate.timeCommitment = cleaned_data.get('timeCommitment')
            candidate.transcript = cleaned_data.get('transcript')
            candidate.save()

            for lan in self.languageFieldsNames:
                language = Language()
                language.language = cleaned_data.get(lan['language'])
                language.fluency = cleaned_data.get(lan['proficiency'])
                language.details = cleaned_data.get(lan['details'])
                language.user = user
                language.save()

        return user


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=MAX_LENGTH_STANDARDFIELDS,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
                            )

    password = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))