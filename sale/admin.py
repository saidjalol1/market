from django.contrib import admin
from .models import Check, CheckItem

# Register your models here.
admin.site.register(Check)
admin.site.register(CheckItem)