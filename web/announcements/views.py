from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render

from companies.models import Company
from jobapplications.models import JobApplication
from joblistings.models import Job
from accounts.models import Candidate
from django.http import HttpResponseRedirect
from notifications.models import Notification
from django.db.models import Q

# Create your views here.
def view_notifications(request, searchString= ""):
    context = {}

    if request.user.is_authenticated:
        context["newMessageCount"] = len(request.user.notifications.unread())
        if searchString:
            searchWords = searchString.split("&")
        else:
            searchWords = []

        search = {}

        for searchWord in searchWords:
            pair = searchWord.split("=")
            if len(pair) == 2:
                search[pair[0]] = pair[1]

        user = request.user

        notifications = []
        if "type" in search:   
            if search["type"] == "All":
                notifications = user.notifications.all()
            if search["type"] == "New":
                notifications = user.notifications.unread()
            if search["type"] == "Seen":
                notifications = user.notifications.read()
            if search["type"] == "MarkRead":
                user.notifications.mark_all_as_read()
                notifications = user.notifications.all()
        else:
            notifications = user.notifications.all()

        if "redirectHome" in search:
            return HttpResponseRedirect("/") 

        currentId = -1
        if "view" in search:
            try:
                currentId = int(search["view"])
            except:
                pass

        query = Q()

        if currentId != -1:
            query = Q(pk = currentId)
            currentNotification = get_object_or_404(Notification, query)
            currentNotification.unread = False
            currentNotification.save()
            context["showNotification"] = currentNotification

        context["notificationList"] = notifications
        context["currentId"] = currentId

        
        return render(request, "dashboard-message.html", context)
    else:
        return HttpResponseRedirect("/login")