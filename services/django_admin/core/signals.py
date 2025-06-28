import os
import json

from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import VideoUpload

from ffmpeg import FFmpeg

@receiver(pre_save, sender=VideoUpload)
def video_info(sender, instance, **kwargs):

    if instance.file and not instance.duration:

        local_path = instance.file.path

        try:

            ffprobe = FFmpeg(executable="ffprobe").input(
                url          = local_path,
                print_format ="json",
                show_streams = None,
            )

            media           = json.loads(ffprobe.execute())
            duration        = float(media["streams"][0]["duration"])
            total_frames    = int(media["streams"][0]["nb_frames"])
            frame_rate      = int(total_frames / duration)
            width           = int(media["streams"][0]["width"])
            height          = int(media["streams"][0]["height"])
            file_format     = os.path.splitext(local_path)[1][1:]
            file_name       = os.path.basename(local_path) 

            instance.duration       = duration
            instance.file_name      = file_name
            instance.file_format    = file_format
            instance.duration       = duration
            instance.frame_rate     = frame_rate
            instance.total_frames   = total_frames
            instance.width          = width
            instance.height         = height

        except Exception as e:
            print(f"Error: failed to extract metadata from video ({e}).")

