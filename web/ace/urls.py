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


from view import home_page
from joblistings.views import job_details, post_job, download_jobPDF, manage_jobs, job_search
from jobapplications.views import add_resume, download_test, browse_job_applications, get_protected_file, get_protected_file_withAuth, view_application_details
from accounts.views import register_user, logout_user, login_user, activate
from django.urls import include
from django.urls import register_converter

from jobmatchings.views import employer_view_rankings, candidate_view_rankings, admin_matchmaking, view_matching

class OptionalIntConverter:
    regex = '[0-9]*'
 
    def to_python(self, value):
        if value:
            return int(value)
        else:
            return None
 
    def to_url(self, value):
        return str(value) if value is not None else ''
 
register_converter(OptionalIntConverter, 'optional_int')

urlpatterns = [
    path('', home_page),
    path('admin/', admin.site.urls),
    path('job-details/<int:pk>/', job_details),
    path('employer-dashboard-post-job/', post_job),
    path('add-resume/<int:pk>/', add_resume),
    path('tinymce', include('tinymce.urls')),
    path('test/<int:pk>/', download_test),
    path('jobDescription/<int:pk>/', download_jobPDF),
    path('register/', register_user),
    path('logout/', logout_user),
    path('login/', login_user),
    path('activate/<uidb64>/<token>', activate, name="activate"),
    path('search/', job_search),
    path('jobApplications/<optional_int:jobId>', browse_job_applications),
    path('jobApplications/<optional_int:jobId>/<slug:searchString>', browse_job_applications),
    path('jobApplications/<slug:searchString>', browse_job_applications),
    path('jobApplicationDetails/<int:pk>/', view_application_details),
    path('getFile/<str:uid>/<str:candidateId>/<str:filetype>/<str:fileid>/<token>/', get_protected_file),
    path('manageJobs/', manage_jobs),
    path('employerRanking/<optional_int:jobId>', employer_view_rankings),
    path('candidateRanking/', candidate_view_rankings),
    path('matchDay/', admin_matchmaking),
    path('viewMatch/<optional_int:jobId>', view_matching),
    path('getFileWithAuth/<int:fileType>/<int:applicationId>/', get_protected_file_withAuth),

]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
