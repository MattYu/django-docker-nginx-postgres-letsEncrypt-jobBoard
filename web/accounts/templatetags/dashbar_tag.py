from django import template
from joblistings.models import Job
from companies.models import Company



register = template.Library()

@register.inclusion_tag('dashbar.html')
def get_dashbar(*args, **kwargs):


    location = kwargs['location']

    return {
        'location': location
    }