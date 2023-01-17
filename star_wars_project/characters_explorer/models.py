from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from petl import tocsv

import os
import hashlib
# Create your models here.


class Characters(models.Model):
    """
    Model representing characters csv file
    """    
    download_date = models.DateTimeField()
    file_name = models.CharField(max_length=256, unique=True)
    folder_path = models.CharField(max_length=256)

    def __str__(self):
        """
        Method to show download date upon print

        Returns:
            str: string containing formatted date
        """        
        return self.download_date.strftime("%b. %d, %Y, %I:%M %p")

    def save(self, *args, **kwargs):
        """
        Overrides model's save method to save characters table csv upon saving the model to database 

        Raises:
            ValidationError: when no table was provided
        """        
        try:
            table = kwargs.pop('characters_table')
            m = hashlib.md5()
            m.update(bytes(self.download_date.strftime(
                "%d%m%Y%H%M%S%f"), encoding='utf-8'))
            self.file_name = (m.hexdigest()) + ".csv"

            tocsv(table, settings.MEDIA_ROOT.joinpath(
                self.folder_path, self.file_name))
        except KeyError:
            raise ValidationError('Petl table containing characters required')

        super(Characters, self).save(*args, **kwargs)


@receiver(post_delete, sender=Characters)
def delete_characters_csv(sender, instance, **kwargs):
    """
    Method run after model instance was deleted to remove the csv file as well.
    Post_delete signal was used instead of overriding delete method. The reason being when multiple
    model instances are removed delete method is not called but signals are sent

    Args:
        sender (Characters): Signals sender
        instance (Characters): Instance of the deleted model
    """
    file_path = settings.MEDIA_ROOT.joinpath(
        instance.folder_path, instance.file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    else:
        print(
            f"File: {file_path} doesn't exist, so it will not be removed along model")
