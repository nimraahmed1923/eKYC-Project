from django.contrib import admin
from .models import EkycData

@admin.register(EkycData)
class EkycDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'document_type', 'aadhaar_number', 'pan_number', 'passport_number', 'timestamp')
    search_fields = ('name', 'aadhaar_number', 'pan_number', 'passport_number')
    list_filter = ('document_type',)