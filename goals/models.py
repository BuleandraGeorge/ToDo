from django.db import models
from django.utils import timezone
from userProfile.models import profile


class goal(models.Model):
    title=models.CharField(max_length=255, null=False, blank=False)
    description=models.TextField(max_length=1000, null=False, blank=True)
    start_date=models.DateTimeField(default=timezone.now, null=False, blank=False)
    end_date=models.DateTimeField(default=timezone.now, null=False, blank=False)
    owner = models.ForeignKey(profile, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

class task(models.Model):
    content=models.TextField(max_length=1000, null=False, blank=True)
    done=models.BooleanField(default=False)
    goal=models.ForeignKey(goal, on_delete=models.CASCADE)

    def __str__(self):
        return self.pk