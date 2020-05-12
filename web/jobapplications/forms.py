from django import forms
from ace.constants import CATEGORY_CHOICES, MAX_LENGTH_STANDARDFIELDS, MAX_LENGTH_LONGSTANDARDFIELDS
from jobapplications.models import JobApplication, Education, Experience, Resume, SupportingDocument, CoverLetter
from tinymce.widgets import TinyMCE
from django.core.validators import FileExtensionValidator
from django.shortcuts import get_object_or_404
from joblistings.models import Job
from accounts.models import Candidate
import uuid
from django.db.models import Q
import os

from django.core.files.storage import FileSystemStorage

#jobApplication = JobApplication.objects.filter(job__pk=pk, candidate=Candidate.objects.get(user=request.user)).count()
'''
    def __init__(self, *args, **kwargs):
        jobId = kwargs.pop('jobId', None)
        super().__init__(*args, **kwargs)

        if jobId:

            currentPermission = []

            job = Job.objects.filter(pk= jobId).all()[0]
            employerSet = set()
            for employer in job.jobAccessPermission.all():
                currentPermission.append((employer.pk, employer.user.email))
                employerSet.add(employer)

            employerOfSameCompanyWithoutPermission = Employer.objects.filter(company = job.company).all()

            sameCompany = []

            for employer in employerOfSameCompanyWithoutPermission.all():
                if employer not in employerSet:
                    sameCompany.append((employer.pk, employer.user.email))

            sorted(currentPermission, key=lambda x: x[1])
            sorted(sameCompany, key=lambda x: x[1])
            currentPermission.insert(0, ("Remove Permission", "Revoke Permission"))
            sameCompany.insert(0, ("Add Permission", "Add Permission from " + job.company.name))
            self.fields['addEmployer'].choices = sameCompany
            self.fields['removeEmployer'].choices = currentPermission
'''
'''
    educations = Education.objects.filter(JobApplication=jobApplication).all()

    experience = Experience.objects.filter(JobApplication=jobApplication).all()
'''

class resumeUpload(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ('resume',)

class documentUpload(forms.ModelForm):
    class Meta:
        model = SupportingDocument
        fields = ('document',)

class documentUpload(forms.ModelForm):
    class Meta:
        model = CoverLetter
        fields = ('coverLetter',)

class ApplicationForm(forms.Form):

    numberOfEduForms = 1
    numberOfCVForm = 1
    numberOfCoverLetterForm = 1

    extra_edu_count = forms.IntegerField(widget=forms.HiddenInput())
    extra_exp_count = forms.IntegerField(widget=forms.HiddenInput())
    extra_doc_count = forms.IntegerField(widget=forms.HiddenInput())

    oldResumes = forms.ChoiceField(
        required = False,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Resume'})
    )


    firstName = forms.CharField(max_length=MAX_LENGTH_STANDARDFIELDS,
                                required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
                                )

    lastName = forms.CharField(max_length=MAX_LENGTH_STANDARDFIELDS, required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
                                )
    
    preferredName = forms.CharField(max_length=MAX_LENGTH_STANDARDFIELDS, required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preferred First Name (optional)'})
                                )


    #resume = resumeUpload()
    resume = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'add-new-field'}))
    #coverLetter = documentUpload()
    coverLetter = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'add-new-field'}))

    class Meta:
        model = JobApplication

    def __init__(self, *args, **kwargs):

        initWithHistory = kwargs.pop('initWithHistory', True)
        self.educationFields = []
        self.educationFieldsNames = []
        self.experienceFields = [] 
        self.experienceFieldsNames = []
        user = kwargs.pop('user', None)
        educations = None
        experience = None
        if initWithHistory:
            jobApplication = JobApplication.objects.filter(candidate=Candidate.objects.get(user=user)).order_by("-created_at").first()

            educations = Education.objects.filter(JobApplication=jobApplication).distinct()
            experience = Experience.objects.filter(JobApplication=jobApplication).distinct()
            supportingDocuments = SupportingDocument.objects.filter(JobApplication=jobApplication).distinct()
            kwargs.pop('extra_edu_count', 1)
            kwargs.pop('extra_exp_count', 1)
            kwargs.pop('extra_doc_count', 0)
            extra_edu_fields = max(len(educations), 1)
            extra_exp_fields = max(len(experience), 1)
            extra_doc_fields = max(len(supportingDocuments), 0)
        else:
            extra_edu_fields = kwargs.pop('extra_edu_count', 1)
            extra_exp_fields = kwargs.pop('extra_exp_count', 1)
            extra_doc_fields = kwargs.pop('extra_doc_count', 0)

        super().__init__(*args, **kwargs)
    
        if user:
            self.fields['firstName'].initial = user.firstName
            self.fields['lastName'].initial = user.lastName
            self.fields['preferredName'].initial = user.preferredName

        self.fields['extra_edu_count'].initial = max(min(int(extra_edu_fields), 10),1)
        for i in range(int(self.fields['extra_edu_count'].initial)):
            if initWithHistory and len(educations) > i:
                self.add_education(i,  education=educations[i])
            else:
                self.add_education(i)

        self.fields['extra_exp_count'].initial = max(min(int(extra_exp_fields), 10),1)
        for i in range(int(self.fields['extra_exp_count'].initial)):
            if initWithHistory and len(experience) > i:
                self.add_experience(i, experience=experience[i])
            else:
                self.add_experience(i)

        
        self.fields['extra_doc_count'].initial = max(min(int(extra_doc_fields), 10), 0)
        self.documentsFields = []
        self.documentsFieldsNames = []
        for i in range(int(self.fields['extra_doc_count'].initial)):
            self.add_document(i)


        currentOptions = []
        resumes = Resume.objects.filter(candidate= Candidate.objects.get(user=user)).order_by("-created_at").distinct()
        for resume in resumes:
            currentOptions.append((resume.pk, os.path.basename(resume.resume.file.name)))

        currentOptions.insert(0, ("OR Select an Existing CV from the List", "OR Select an Existing CV from the List"))
        self.fields['oldResumes'].choices = currentOptions

    def get_education_fields(self):
        return self.educationFields

    def get_experience_fields(self):
        return self.experienceFields

    def get_document_fields(self):
        return self.documentsFields

    def add_education(self, i:int = None, education = None):
        if i == None:
            i = len(self.educationFields)
        field_name = '_educations_%s' % (i,)
        educationDict = {}
        eduNameDict = {}
        self.fields['institute' + field_name] = forms.CharField(
                                                                    max_length=MAX_LENGTH_STANDARDFIELDS,
                                                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Institute'})
                                                                )
        educationDict['institute'] = self['institute' + field_name]
        eduNameDict['institute'] = 'institute' + field_name
        self.fields['title' + field_name] = forms.CharField(
                                                                    max_length=MAX_LENGTH_STANDARDFIELDS,
                                                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Degree'})
                                                            )
        educationDict['title'] = self['title' + field_name]
        eduNameDict['title'] = 'title' + field_name
        self.fields['period' + field_name] = forms.CharField(
                                                                    max_length=MAX_LENGTH_STANDARDFIELDS,
                                                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Period'})
                                                            )
        educationDict['period'] = self['period' + field_name]
        eduNameDict['period'] = 'period' + field_name
        self.fields['description' + field_name] = forms.CharField(
                                                                    max_length=MAX_LENGTH_LONGSTANDARDFIELDS,
                                                                    required= False,
                                                                    widget=TinyMCE(attrs={'class': 'form-control', 'placeholder': 'Description (Optional)'})
                                                                )
        educationDict['description'] = self['description' + field_name]
        eduNameDict['description'] = 'description' + field_name
        
        self.educationFields.append(educationDict)
        self.educationFieldsNames.append(eduNameDict)

        if education:
            self.fields['institute' + field_name].initial = education.institute
            self.fields['title' + field_name].initial = education.title
            self.fields['period' + field_name].initial = education.period
            self.fields['description' + field_name].initial = education.description

        return educationDict

    def add_experience(self, i:int, experience=None):
        field_name = '_experience_%s' % (i,)
        experienceDict = {}
        expNameDict = {}
        self.fields['companyName' + field_name] = forms.CharField(
                                                                    max_length=MAX_LENGTH_STANDARDFIELDS,
                                                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company'})
                                                                )
        experienceDict['companyName'] = self['companyName' + field_name]
        expNameDict['companyName'] = 'companyName' + field_name
        self.fields['title' + field_name] = forms.CharField(
                                                                    max_length=MAX_LENGTH_STANDARDFIELDS,
                                                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job title'})
                                                            )
        experienceDict['title'] = self['title' + field_name]
        expNameDict['title'] = 'title' + field_name
        self.fields['period' + field_name] = forms.CharField(
                                                                    max_length=MAX_LENGTH_STANDARDFIELDS,
                                                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Period'})
                                                            )
        experienceDict['period'] = self['period' + field_name]
        expNameDict['period'] = 'period' + field_name
        self.fields['description' + field_name] = forms.CharField(
                                                                    max_length=MAX_LENGTH_LONGSTANDARDFIELDS,
                                                                    required= False,
                                                                    widget=TinyMCE(attrs={'class': 'form-control', 'placeholder': 'Description (Optional)'})
                                                                )
        experienceDict['description'] = self['description' + field_name]
        expNameDict['description'] = 'description' + field_name

        self.experienceFields.append(experienceDict)
        self.experienceFieldsNames.append(expNameDict)

        if experience:
            self.fields['companyName' + field_name].initial = experience.companyName
            self.fields['title' + field_name].initial = experience.title
            self.fields['period' + field_name].initial = experience.period
            self.fields['description' + field_name].initial = experience.description

        return experienceDict


    def add_document(self, i:int):
        field_name = '_doc_%s' % (i,)
        docDict = {}
        docName = {}
        self.fields['name' + field_name] = forms.CharField(
                                                                    max_length=MAX_LENGTH_STANDARDFIELDS,
                                                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supporting document name / type'})
                                                                )
        docDict['name'] = self['name' + field_name]
        docName['name'] = 'name' + field_name
        self.fields['file' + field_name] = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'add-new-field'}))
        docDict['file'] = self['file' + field_name]
        docName['file'] = 'file' + field_name
        
        self.documentsFields.append(docDict)
        self.documentsFieldsNames.append(docName)

        return docDict

    def clean(self):
        self.raise_errors = []
        cleaned_data = super().clean()
        for error in self._errors:
            import sys
            print(error, file=sys.stderr)
            print(self._errors[error], file=sys.stderr)

        if not cleaned_data.get('resume') and self.is_valid() and cleaned_data.get("oldResumes") == "OR Select an Existing CV from the List":
            self.raise_errors.append('You have to upload a resume')
        
        if not cleaned_data.get('coverLetter') and self.is_valid():
             self.raise_errors.append('You have to upload a cover letter')
        
        if cleaned_data.get('resume') and self.is_valid() and cleaned_data.get("oldResumes") != "OR Select an Existing CV from the List":
            if not cleaned_data.get('resume').name.endswith(".pdf"):
                 self.raise_errors.append('Files must be in pdf format')
        if self.is_valid() and cleaned_data.get('coverLetter') and not cleaned_data.get('coverLetter').name.endswith(".pdf"):
             self.raise_errors.append('Files must be in pdf format')
        
        '''
        for doc in self.documentsFieldsNames:
            if doc and cleaned_data.get(doc['name']) and not cleaned_data.get(doc['name']).endswith(".pdf"):
                raise forms.ValidationError('Files must be in pdf format')
        '''
        if self.raise_errors:
            raise forms.ValidationError(self.raise_errors)
        
        self.cleaned_data = cleaned_data

    def save(self, pk, user):

        jobApplication = JobApplication()
        cleaned_data = self.cleaned_data
        jobApplication.firstName = user.firstName
        jobApplication.lastName = user.lastName
        jobApplication.preferredName = user.preferredName
        jobApplication.job = get_object_or_404(Job, pk=pk.pk)
        jobApplication.candidate = Candidate.objects.get(user=user)
        jobApplication.save()

        candidate=Candidate.objects.get(user=user)

        if cleaned_data.get("oldResumes") != "OR Select an Existing CV from the List":
            resume = Resume.objects.filter(candidate=Candidate.objects.get(user=user)).first()
            resume.JobApplication.add(jobApplication)
            resume.save()
        else: 
            resume = Resume()
            resume.candidate = candidate
            resume.fileName = cleaned_data.get('resume').name
            resume.resume = cleaned_data.get('resume')
            resume.save()
            resume.JobApplication.add(jobApplication)
            resume.save()

        coverLetter = CoverLetter()
        coverLetter.candidate = candidate
        coverLetter.fileName = cleaned_data.get('coverLetter').name
        coverLetter.coverLetter = cleaned_data.get('coverLetter')
        coverLetter.save()
        coverLetter.JobApplication.add(jobApplication)
        coverLetter.save()


        for edu in self.educationFieldsNames:
            education = Education()
            education.institute = cleaned_data.get(edu['institute'])
            education.title = cleaned_data.get(edu['title'])
            education.period = cleaned_data.get(edu['period'])
            education.description = cleaned_data.get(edu['description'])
            education.save()
            education.JobApplication.add(jobApplication)
            education.save()

        for exp in self.experienceFieldsNames:
            experience = Experience()
            experience.companyName = cleaned_data.get(exp['companyName'])
            experience.title = cleaned_data.get(exp['title'])
            experience.period = cleaned_data.get(exp['period'])
            experience.description = cleaned_data.get(exp['description'])
            experience.save()
            experience.JobApplication.add(jobApplication)
            experience.save()

        for doc in self.documentsFieldsNames:
            try:
                document = SupportingDocument()
                document.candidate = candidate
                document.fileName = cleaned_data.get(doc['name'])
                document.document = cleaned_data.get(doc['file'])
                document.JobApplication.add(jobApplication)
                document.save()
            except:
                pass


        return jobApplication
        '''
        firstName
        lastName
        preferredName
        '''

class FilterApplicationForm(forms.Form):
    selected_filter = forms.CharField(widget=forms.HiddenInput(), required= False,)
    selected_filter_outerHTML = forms.CharField(widget=forms.HiddenInput(), required= False,)
    selected_filter_class = forms.CharField(widget=forms.HiddenInput(), required= False,)
    gpa_min = forms.FloatField(widget=forms.HiddenInput(), required= False,)
    gpa_max = forms.FloatField(widget=forms.HiddenInput(), required= False,)

    firstName = forms.CharField(max_length=MAX_LENGTH_STANDARDFIELDS,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
                                required= False,
                                )

    lastName = forms.CharField(max_length=MAX_LENGTH_STANDARDFIELDS,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
                                required= False,
                                )


    email = forms.CharField(max_length=MAX_LENGTH_STANDARDFIELDS,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
                                required= False,
                                )

    studentId = forms.CharField(max_length=MAX_LENGTH_STANDARDFIELDS,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student ID'}),
                                required= False,
                                )

    program = forms.ChoiceField(
                                choices=CATEGORY_CHOICES,
                                widget=forms.Select(attrs={'class': 'form-control'}),
                                required= False,
                                )

    def getSelectedFilterAsSet(self):
        if self['selected_filter'] != None:
            return set(str(self['selected_filter'].value()).split(","))
        return None

    def getSelectedFilterHTMLAsList(self):
        if self['selected_filter_outerHTML']:
            return str(self['selected_filter_outerHTML'].value()).split(",")
        return None

    def getSelectedFilterClassAsList(self):
        if self['selected_filter_class']:
            return str(self['selected_filter_class'].value()).split(",")
        return None

    def getSelectedFilterPair(self):
        html = self.getSelectedFilterHTMLAsList()
        classes = self.getSelectedFilterClassAsList()

        return list(zip(classes, html))