from django.contrib import admin
from jobmatchings.models import MatchingHistory, Match

# Register your models here.
admin.site.register(Match)
admin.site.register(MatchingHistory)