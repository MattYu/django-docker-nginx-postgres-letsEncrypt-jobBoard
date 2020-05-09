from django import template
from joblistings.models import Job
from companies.models import Company
from django.db.models import Q

register = template.Library()

@register.inclusion_tag('joblist_view.html')
def get_joblist(*args, **kwargs):
    queryset = None
    origin = kwargs["origin"]
    if (origin == "main_page"):
        query =(Q(status= "Approved") | Q(status="Interviewing") | Q(status="Filled") | Q(status="Partially Filled") | Q(status="Closed"))
        queryset = Job.objects.filter(query).order_by('-created_at')[:10]

    return {
        'joblist': queryset
    }