from django.contrib import admin
from jobapplications.models import JobApplication, Education, Experience, SupportingDocument, CoverLetter, Resume, Ranking

# Register your models here.
admin.site.register(JobApplication)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(SupportingDocument)
admin.site.register(CoverLetter)
admin.site.register(Resume)
admin.site.register(Ranking)