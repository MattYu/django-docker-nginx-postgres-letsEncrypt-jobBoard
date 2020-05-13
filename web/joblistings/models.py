from django.db import models
from companies.models import Company
from tinymce import models as tinymce_models
from ace.constants import MONTREAL_LAT, MONTREAL_LNG, MAX_LENGTH_TITLE, MAX_LENGTH_DESCRIPTION, MAX_LENGTH_RESPONSABILITIES, MAX_LENGTH_REQUIREMENTS, MAX_LENGTH_STANDARDFIELDS, CATEGORY_CHOICES, LOCATION_CHOICES, JOB_STATUS
from accounts.models import Employer
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Job(models.Model):
    title = models.CharField(max_length = MAX_LENGTH_TITLE)
    
    #Job Summary

    category = ArrayField(models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "Any", choices= CATEGORY_CHOICES))
    salaryRange = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "N/A", blank=True)
    vacancy = models.IntegerField(null= True, default= 0)
    filled = models.IntegerField(null= True, default= 0)
    startDate = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    expirationDate = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    duration = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")


    description = tinymce_models.HTMLField(max_length = MAX_LENGTH_DESCRIPTION, default= "")
    responsabilities = tinymce_models.HTMLField(max_length = MAX_LENGTH_RESPONSABILITIES, default= "")
    requirements = tinymce_models.HTMLField(max_length = MAX_LENGTH_REQUIREMENTS, default= "")

    status = models.CharField(max_length = 20, default= "Pending", choices= JOB_STATUS)

    # Job Location
    country = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "Canada", choices= LOCATION_CHOICES)
    location = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "Montreal")
    postcode = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    yourLocation = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")

    company = models.ForeignKey(Company, on_delete=models.CASCADE, default= "")

    addressLat = models.FloatField(max_length=20, default=MONTREAL_LAT)
    addressLat = models.FloatField(max_length=20, default=MONTREAL_LNG)
    jobAccessPermission = models.ManyToManyField(Employer, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_fields_and_values(self):
        return [(field, field.value_to_string(self)) for field in Job._meta.fields]

#class Company(models.Model):

class JobPDFDescription(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, default= "")
    descriptionFile = models.FileField(upload_to='company/jobDescription.', default="")

    def __str__(self):
        return self.job.title


    



