import factory
from decimal import Decimal
from datetime import date
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from inmaticpart2.models import InvoiceModel

class InvoiceModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvoiceModel

    # Provide a default value for 'number' at creation time.
    # We can use a dummy pk like 1 for the default to ensure it is never None.
    number = f"F2023/{1:02d}"  # Temporary default, will be updated after creation
    provider = "Telefónica"
    concept = "Sample concept for invoice."
    base_value = Decimal('100.00')
    vat = Decimal('21.00')
    total_value = base_value + (base_value * vat / Decimal('100'))  # Direct calculation
    date = date(2023, 1, 15)
    state = InvoiceStates.DRAFT

    @classmethod
    def build_invoice(cls):
        # Create the invoice with a default value for 'number'
        invoice = cls.create(
            provider=cls.provider,
            concept=cls.concept,
            base_value=cls.base_value,
            vat=cls.vat,
            total_value=cls.total_value,  # Use the calculated total_value directly
            date=cls.date,
            state=cls.state
        )

        # After creation, we generate a proper invoice number using invoice.pk
        invoice.number = f"F2023/{invoice.pk:02d}"

        # Save the invoice with the correct 'number'
        invoice.save()

        return invoice
