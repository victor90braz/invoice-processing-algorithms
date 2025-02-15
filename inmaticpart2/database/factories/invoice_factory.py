import factory
from decimal import Decimal
from datetime import date as datetime_date
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from inmaticpart2.models import InvoiceModel


class InvoiceModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvoiceModel

    number = factory.Sequence(lambda n: f"F2023/{n + 1:02d}")  # Auto-generate unique numbers
    supplier = "Telefónica"
    concept = "Sample concept for invoice."
    base_value = Decimal('100.00')
    vat = Decimal('21.00')
    total_value = base_value + (base_value * vat / Decimal('100'))
    date = datetime_date(2023, 1, 15)  # Use datetime_date here
    state = InvoiceStates.DRAFT

    @classmethod
    def build_invoice(cls, supplier=None, date=None):
        """
        Build and return an InvoiceModel instance.
        :param supplier: Optional supplier name.
        :param date: Optional invoice date.
        """
        # Ensure date is a datetime.date object, not a string
        invoice_date = date or cls.date
        if isinstance(invoice_date, str):
            invoice_date = datetime_date.fromisoformat(invoice_date)

        invoice = cls.create(
            supplier=supplier or cls.supplier,
            concept=cls.concept,
            base_value=cls.base_value,
            vat=cls.vat,
            total_value=cls.total_value,
            date=invoice_date,
            state=cls.state
        )
        return invoice