from django.db import models
from ace.constants import CATEGORY_CHOICES, MAX_LENGTH_STANDARDFIELDS, MAX_LENGTH_STANDARDTEXTAREA, MAX_LENGTH_LONGSTANDARDFIELDS, JOB_APPLICATION_STATUS
from joblistings.models import Job
from accounts.models import Candidate, User
from tinymce import models as tinymce_models

# Create your models here.

class JobApplication(models.Model):

    firstName = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS,  default= "")
    lastName = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS,  default= "")
    #preferredName = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS,  default= "")
    #studentID = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS,  default= "")
    #category = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "Any", choices= CATEGORY_CHOICES)
    #location = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, default= "")
    #skillList = models.CharField(max_length = MAX_LENGTH_LONGSTANDARDFIELDS,  default= "")
    #aboutYou = tinymce_models.HTMLField(max_length = MAX_LENGTH_STANDARDTEXTAREA, default= "")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, default= "1")
    status = models.CharField(max_length = 20, default= "Pending Review", choices= JOB_APPLICATION_STATUS)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.job.title + "[" + str(self.job.pk) + "]" + ' - ' + self.job.company.name + " : " + self.candidate.user.email

class Education(models.Model):
    institute = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    title = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    period = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    description = tinymce_models.HTMLField(max_length = MAX_LENGTH_STANDARDTEXTAREA, default= "")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    JobApplication = models.ManyToManyField(JobApplication)

class Experience(models.Model):
    companyName = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    title = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    period = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    description = tinymce_models.HTMLField(max_length = MAX_LENGTH_STANDARDTEXTAREA, default= "")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    JobApplication = models.ManyToManyField(JobApplication)

class Resume(models.Model):
    fileName = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    resume = models.FileField(upload_to='user/resume/', default= "")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    JobApplication = models.ManyToManyField(JobApplication)

class SupportingDocument(models.Model):
    fileName = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    document = models.FileField(upload_to='user/document/', default= "")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    JobApplication = models.ManyToManyField(JobApplication)

class CoverLetter(models.Model):
    fileName = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    coverLetter = models.FileField(upload_to='user/coverletter/', default= "")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    JobApplication = models.ManyToManyField(JobApplication)

    
class Ranking(models.Model):

    employerRank = models.IntegerField(default= 1000)
    candidateRank = models.IntegerField(default= 1000)

    jobApplication = models.ForeignKey(JobApplication, on_delete=models.CASCADE, default= "")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, default= "")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, default= "")
    status = models.CharField(max_length = 20, default= "Interviewing", choices= JOB_APPLICATION_STATUS)

    is_ranking_open_for_employer = models.BooleanField(default=True)
    is_ranking_open_for_candidate = models.BooleanField(default=False)

    is_closed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.status + " - Employer: " + str(self.employerRank) + ' - Candidate:' + str(self.candidateRank) + " - " + self.candidate.user.lastName + " " + self.candidate.user.firstName +  " [" + self.candidate.user.email + "] applied to " + self.job.title + "[" + str(self.job.id) + "] at " + self.job.company.name 