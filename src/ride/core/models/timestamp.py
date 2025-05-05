from django.db import models
from django.contrib.auth.models import User

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_created_by', null=True, blank=True)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_modified_by', null=True, blank=True)

    class Meta:
        abstract = True