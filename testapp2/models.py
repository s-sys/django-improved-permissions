from django.db import models


class Library(models.Model):
    title = models.CharField(max_length=256)
