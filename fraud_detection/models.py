from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True, blank=True)

    def approve(self):
        self.is_approved = True
        self.approval_date = timezone.now()
        self.save()

class TrainedModel(models.Model):
    name = models.CharField(max_length=100)
    algorithm = models.CharField(max_length=100)
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    auc_roc = models.FloatField()
    accuracy = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)
    model_file = models.FileField(upload_to='models/')
    preprocessor_file = models.FileField(upload_to='models/', null=True, blank=True)

    def __str__(self):
        return f"{self.algorithm} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class PredictionHistory(models.Model):
    model = models.ForeignKey(TrainedModel, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    input_data = models.JSONField()
    prediction = models.BooleanField()
    prediction_probability = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Prediction {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
