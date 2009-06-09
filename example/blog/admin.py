from django.contrib import admin
from example.blog.models import Entry, Topic, Link

admin.site.register(Entry)
admin.site.register(Topic)
admin.site.register(Link)
