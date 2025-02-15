import factory
from decimal import Decimal
from datetime import date
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from inmaticpart2.models import InvoiceModel

class InvoiceModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvoiceModel

    number = f"F2023/{1:02d}"
    supplier = "Telefónica"
    concept = "Sample concept for invoice."
    base_value = Decimal('100.00')
    vat = Decimal('21.00')
    total_value = base_value + (base_value * vat / Decimal('100'))
    date = date(2023, 1, 15)
    state = InvoiceStates.DRAFT

    @classmethod
    def build_invoice(cls):
        invoice = cls.create(
            supplier=cls.supplier,
            concept=cls.concept,
            base_value=cls.base_value,
            vat=cls.vat,
            total_value=cls.total_value,
            date=cls.date,
            state=cls.state
        )

        invoice.number = f"F2023/{invoice.pk:02d}"

        invoice.save()

        return invoice
