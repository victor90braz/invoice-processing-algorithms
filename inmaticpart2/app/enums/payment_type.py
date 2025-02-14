from django.db import models

class PaymentType(models.TextChoices):
    DEBIT = "DEBIT", 'Debit'
    CREDIT = "CREDIT", 'Credit'
