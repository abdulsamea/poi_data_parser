from django.contrib import admin
from .models import Poi

@admin.register(Poi)
class PoiAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "external_id", "category", "avg_rating")
    list_filter = ("category",)
    search_fields = ("id", "external_id", "name")
    readonly_fields = ("created_at", "updated_at")
