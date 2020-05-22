from django.contrib import admin
from announcements.models import Event, RankingMessage, MatchingMessage, GlobalAnnouncement, MainPageVideo


# Register your models here.
admin.site.register(Event)
admin.site.register(RankingMessage)
admin.site.register(MatchingMessage)
admin.site.register(GlobalAnnouncement)
admin.site.register(MainPageVideo)
