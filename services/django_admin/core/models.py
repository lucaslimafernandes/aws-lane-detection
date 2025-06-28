from django.db import models
from django.contrib.auth.models import User


class VideoUpload(models.Model):

    upload_user  = models.ForeignKey(User, on_delete=models.CASCADE)
    file         = models.FileField(upload_to="videos/")
    file_name    = models.CharField(max_length=255)
    file_format  = models.CharField(max_length=10)
    duration     = models.FloatField(help_text="Duration in seconds")
    frame_rate   = models.FloatField()
    total_frames = models.IntegerField()
    width        = models.IntegerField()
    height       = models.IntegerField()
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name
