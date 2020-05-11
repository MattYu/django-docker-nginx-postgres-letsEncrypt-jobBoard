from django.db import models
from accounts.models import Candidate, Employer, User
from tinymce import models as tinymce_models
from ace.constants import MAX_LENGTH_TERMSANDCONDITIONS, MAX_LENGTH_STANDARDFIELDS

class Candidate_termsAndConditions(models.Model):
    title = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    description = tinymce_models.HTMLField(max_length = MAX_LENGTH_TERMSANDCONDITIONS, default= "")
    agreedList = models.ManyToManyField(Candidate, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Employer_termsAndConditions(models.Model):
    title = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    description = tinymce_models.HTMLField(max_length = MAX_LENGTH_TERMSANDCONDITIONS, default= "")
    agreedList = models.ManyToManyField(Employer, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title