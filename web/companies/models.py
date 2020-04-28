from django.db import models
from ace.constants import COMPANY_STATUS

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length = 100, default= "")
    address = models.CharField(max_length = 100, default= "")
    website = models.CharField(max_length = 100, default= "")
    profile = models.TextField(max_length = 1000, default= "")
    videoType = models.CharField(max_length = 30, default= "youtube")
    videoLink = models.CharField(max_length = 200, default= "https://www.youtube.com/watch?v=NwAxNFwEEbM")
    image =   models.ImageField(upload_to='images/company/', default="images/company/company-logo-1")
    status = models.CharField(max_length = 20, default= "Pending", choices= COMPANY_STATUS)
    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name