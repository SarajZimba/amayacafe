from django.contrib import admin

# Register your models here.
from .models import Organization, Branch, Table

admin.site.register([Organization, Branch, Table])
