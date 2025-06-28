from django.db import models
from django.contrib.auth.models import User


class VideoUpload(models.Model):

    upload_user  = models.ForeignKey(User, on_delete=models.CASCADE)
    file         = models.FileField(upload_to="videos/")
    file_name    = models.CharField(max_length=255, blank=True)
    file_format  = models.CharField(max_length=10, blank=True)
    duration     = models.FloatField(help_text="Duration in seconds", blank=True, null=True)
    frame_rate   = models.FloatField(blank=True, null=True)
    total_frames = models.IntegerField(blank=True, null=True)
    width        = models.IntegerField(blank=True, null=True)
    height       = models.IntegerField(blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name
