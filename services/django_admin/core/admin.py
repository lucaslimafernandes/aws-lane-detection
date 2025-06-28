from django.contrib import admin
from .models import VideoUpload


@admin.register(VideoUpload)
class VideoUploadAdmin(admin.ModelAdmin):

    list_display    = ("file_name", "upload_user", "duration", "frame_rate", "total_frames", "created_at")
    readonly_fields = ("duration", "frame_rate", "total_frames")

