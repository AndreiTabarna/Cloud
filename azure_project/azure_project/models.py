from django.db import models

class Photo(models.Model):
    title = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='photos/')

    class Meta:
        db_table = 'azure_project_photo'

