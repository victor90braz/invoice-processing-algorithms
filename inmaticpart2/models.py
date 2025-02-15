from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

class InvoiceModel(models.Model):
    number = models.CharField(max_length=50, default="UNKNOWN")  
    provider = models.CharField(max_length=100)
    concept = models.CharField(max_length=100)
    base_value = models.DecimalField(max_digits=10, decimal_places=2)
    vat = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    state = models.CharField(max_length=50)

    def clean(self):
        super().clean()  
        errors = {}

        # Validate mandatory fields
        if not self.number or self.number == "UNKNOWN":
            errors["number"] = "Invoice number is required."

        if not self.provider:
            errors["provider"] = "Provider is required."

        # Validate other fields
        if self.base_value <= 0:
            errors["base_value"] = "Base value must be greater than zero."

        if self.vat < 0:
            errors["vat"] = "VAT cannot be negative."

        if self.total_value <= 0:
            errors["total_value"] = "Total value must be greater than zero."

        expected_total = self.base_value + self.vat
        if self.total_value != expected_total:
            errors["total_value"] = f"Total value must be {expected_total}."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Invoice {self.pk or 'New'} - {self.provider} ({self.state})"
