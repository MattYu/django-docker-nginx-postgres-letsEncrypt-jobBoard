from django import template
from joblistings.models import Job
from companies.models import Company



register = template.Library()

@register.inclusion_tag('navbar.html')
def get_navbar(*args, **kwargs):
    queryset = None

    user = kwargs["user"]

    notifications = user.notifications.unread()


    return {
        'user': user,
        'notifications': notifications,
        'notificationsCount': len(notifications),
    }