from django.contrib import admin
from .models import Genre, Status, ReadingRecord, Book

admin.site.register(Genre)
admin.site.register(Status)
admin.site.register(ReadingRecord)
admin.site.register(Book)