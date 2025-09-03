from django.db import models

class Poi(models.Model):
    name = models.CharField(max_length=255, blank=True, default="")
    external_id = models.CharField(max_length=64, unique=True, db_index=True)
    category = models.CharField(max_length=64, db_index=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    avg_rating = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name or '(Unnamed)'} [{self.external_id}]"
