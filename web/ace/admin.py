from django.contrib import admin
from jobapplications.models import JobApplication, Education, Experience, SupportingDocument, CoverLetter
from ace.models import Candidate_termsAndConditions, Employer_termsAndConditions

admin.site.register(Candidate_termsAndConditions)
admin.site.register(Employer_termsAndConditions)