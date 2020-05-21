"""ace URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.contrib.auth import views

from ace.views import home_page
from joblistings.views import job_details, post_job, download_jobPDF, manage_jobs, job_search
from jobapplications.views import add_resume, download_test, browse_job_applications, get_protected_file, get_protected_file_withAuth, view_application_details
from companies.views import view_company_details, manage_companies
from accounts.views import edit_candidate_profile, edit_profile, register_user, logout_user, login_user, activate, manage_employers, validate, resend_activation, activate_account, validated
from ace.views import terms_and_conditions
from django.urls import include
from django.urls import register_converter

from jobmatchings.views import employer_view_rankings, candidate_view_rankings, admin_matchmaking, view_matching, admin_open_matching
from announcements.views import view_notifications

import notifications.urls


class OptionalIntConverter:
    regex = '[0-9]*'
 
    def to_python(self, value):
        if value:
            return int(value)
        else:
            return None
 
    def to_url(self, value):
        return str(value) if value is not None else ''

class OptionalStringConverter:
    regex = '[^@]*'
 
    def to_python(self, value):
        if value:
            return str(value)
        else:
            return None
 
    def to_url(self, value):
        return str(value) if value is not None else ''
 
register_converter(OptionalIntConverter, 'optional_int')
register_converter(OptionalStringConverter, 'optional_string')

urlpatterns = [
    path('', home_page),
    path('admin/', admin.site.urls),
    path('job-details/<int:pk>/', job_details),
    path('employer-dashboard-post-job/', post_job),
    path('add-resume/<int:pk>/', add_resume),
    path('tinymce', include('tinymce.urls')),
    path('test/<int:pk>/', download_test),
    path('jobDescription/<int:pk>/', download_jobPDF),
    path('register/<optional_int:employer>', register_user),
    path('logout/', logout_user),
    path('login/', login_user),
    path('accounts/login/', login_user),
    path('activate/<uidb64>/<token>', activate, name="activate"),
    path('activate/', activate_account, name="activate your account"),
    path('resend_activation/', resend_activation, name="resend activation link"),
    path('validate/<uidb64>/<token>', validate, name="validate"),
    path('search/<optional_string:searchString>', job_search),
    path('jobApplications/<optional_int:jobId>', browse_job_applications),
    path('jobApplications/<optional_int:jobId>/<optional_string:searchString>', browse_job_applications),
    path('jobApplications/<optional_string:searchString>', browse_job_applications),
    path('jobApplicationDetails/<int:pk>/', view_application_details),
    path('getFile/<str:uid>/<str:candidateId>/<str:filetype>/<str:fileid>/<token>/', get_protected_file),
    path('manageJobs/<optional_string:searchString>', manage_jobs),
    path('manageCompanies/<optional_string:searchString>', manage_companies),
    path('manageEmployers/<optional_string:searchString>', manage_employers),
    path('employerRanking/<optional_int:jobId>', employer_view_rankings),
    path('candidateRanking/', candidate_view_rankings),
    path('matchDay/', admin_matchmaking),
    path('viewMatch/<optional_int:jobId>', view_matching),
    path('getFileWithAuth/<int:fileType>/<int:applicationId>/<optional_int:supportID>', get_protected_file_withAuth),
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('company-details/<int:pk>/', view_company_details),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('terms-and-conditions/<int:userType>/<int:pk>', terms_and_conditions),
    path('validated/', validated),
    path('notifications/<optional_string:searchString>', view_notifications),
    path('adminOpenMatching/', admin_open_matching),
    path('edit-profile/', edit_profile),
    path('edit-profile/candidateInfo', edit_candidate_profile),
    path('edit-profile/concordiaEmailValidation', edit_profile),
    path('edit-profile/employerInfo', edit_profile),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
