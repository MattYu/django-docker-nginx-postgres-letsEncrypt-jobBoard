from django import forms
from joblistings.models import Job
from accounts.models import Employer
from ace.constants import CATEGORY_CHOICES, MAX_LENGTH_TITLE, MAX_LENGTH_DESCRIPTION, MAX_LENGTH_RESPONSABILITIES, MAX_LENGTH_REQUIREMENTS, MAX_LENGTH_STANDARDFIELDS, LOCATION_CHOICES
from tinymce.widgets import TinyMCE
from companies.models import Company
from joblistings.models import Job, JobPDFDescription
from django.shortcuts import get_object_or_404
from accounts.models import Employer
from django.db.models import Q

class AdminMigrateCompany(forms.Form):
    employer = forms.ChoiceField(
        required = False,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Category'})
    )

    validCompany = forms.ChoiceField(
        required = False,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Category'})
    )


    def __init__(self, *args, **kwargs):
        companyId = kwargs.pop('pk', None)
        super().__init__(*args, **kwargs)

        if companyId:

            currentPermission = []
            validAlternativeCompanies = []

            company = Company.objects.filter(pk= companyId).all()[0]
            companyEmployers = []
            for employer in Employer.objects.filter(Q(company= companyId) & ~Q(status= "Not Approved")).all():
                companyEmployers.append((employer.pk, employer.user.email))

            for company in Company.objects.filter(status = "Approved").order_by('name'):
                validAlternativeCompanies.append((company.pk, company.name))

            sorted(currentPermission, key=lambda x: x[1])
            sorted(validAlternativeCompanies, key=lambda x: x[1])
            currentPermission.insert(0, ("Company's employees", "Company's employees"))
            validAlternativeCompanies.insert(0, ("Approved Companies", "Approved Companies"))
            self.fields['employer'].choices = companyEmployers
            self.fields['validCompany'].choices = validAlternativeCompanies