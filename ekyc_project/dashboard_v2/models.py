from django.db import models

class EkycData(models.Model):
    document_type = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    dob = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    aadhaar_number = models.CharField(max_length=20, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    place_of_birth = models.CharField(max_length=100, blank=True, null=True)
    place_of_issue = models.CharField(max_length=100, blank=True, null=True)
    date_of_issue = models.CharField(max_length=20, blank=True, null=True)
    date_of_expiry = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, default="Clear")
    fraud_score = models.FloatField(default=0.0)  # ← add this line
    timestamp = models.DateTimeField(auto_now_add=True)