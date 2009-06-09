import os
from django.db import models
from vcstorage.fields import VcFileField
from vcstorage.storage import MercurialStorage, GitStorage, BazaarStorage

def handle_attachment(instance, filename):
    return os.path.join(instance.title.lower(), filename)

class Entry(models.Model):
    "Example model that uses the VCSTORAGE_DEFAULT_BACKEND 'hg'"
    title = models.CharField(max_length=100)
    content = models.TextField()
    attachment = VcFileField(upload_to=handle_attachment, storage=MercurialStorage())

    class Meta:
        verbose_name = 'entry'
        verbose_name_plural = 'entries'

class Topic(models.Model):
    "Example model that uses the Git storage backend"
    title = models.CharField(max_length=100)
    content = models.TextField()
    attachment = VcFileField(storage=GitStorage())

    class Meta:
        verbose_name = 'topic'
        verbose_name_plural = 'topics'

class Link(models.Model):
    "Example model that uses the Bazaar storage backend"
    title = models.CharField(max_length=100)
    url = models.URLField()
    attachment = VcFileField(storage=BazaarStorage())

    class Meta:
        verbose_name = 'link'
        verbose_name_plural = 'links'
