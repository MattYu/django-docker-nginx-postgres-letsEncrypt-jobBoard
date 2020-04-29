from django.db import models
from tinymce import models as tinymce_models
from ace.constants import MAX_LENGTH_TITLE, MAX_LENGTH_DESCRIPTION, MAX_LENGTH_RESPONSABILITIES, MAX_LENGTH_REQUIREMENTS, MAX_LENGTH_STANDARDFIELDS, CATEGORY_CHOICES, LOCATION_CHOICES, JOB_STATUS


# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length = MAX_LENGTH_TITLE)
    author = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    description = tinymce_models.HTMLField(max_length = MAX_LENGTH_DESCRIPTION, default= "")
    month = models.CharField(max_length = 3, default= "")
    day = models.CharField(max_length = 2, default= "")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RankingMessage(models.Model):
    title = models.CharField(max_length = MAX_LENGTH_TITLE)
    author = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    description = tinymce_models.HTMLField(max_length = MAX_LENGTH_DESCRIPTION, default= "")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MatchingMessage(models.Model):
    title = models.CharField(max_length = MAX_LENGTH_TITLE)
    author = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    description = tinymce_models.HTMLField(max_length = MAX_LENGTH_DESCRIPTION, default= "")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class GlobalAnnouncement(models.Model):
    title = models.CharField(max_length = MAX_LENGTH_TITLE)
    author = models.CharField(max_length = MAX_LENGTH_STANDARDFIELDS, default= "")
    description = tinymce_models.HTMLField(max_length = MAX_LENGTH_DESCRIPTION, default= "")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)