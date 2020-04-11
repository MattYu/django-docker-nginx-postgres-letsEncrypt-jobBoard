from django import template

register = template.Library()

@register.inclusion_tag('joblist_view.html',takes_context=True)
def job_list(context):
    return {'test':'test'}