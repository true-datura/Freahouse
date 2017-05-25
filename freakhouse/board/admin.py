from django.contrib import admin

from .models import File, FileType, Section, Thread, Post


@admin.register(File, FileType, Section, Thread, Post)
class SectionAdmin(admin.ModelAdmin):
    pass
