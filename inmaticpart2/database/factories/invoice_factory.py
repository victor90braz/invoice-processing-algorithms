import factory
from decimal import Decimal
from datetime import date as datetime_date
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from inmaticpart2.models import InvoiceModel


class InvoiceModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvoiceModel

    # Auto-generate unique invoice numbers
    number = factory.Sequence(lambda n: f"F2023/{n + 1:02d}")
    supplier = "Telefónica"
    concept = "Sample concept for invoice."
    base_value = Decimal('100.00')
    vat = Decimal('21.00')
    total_value = factory.LazyAttribute(lambda o: o.base_value + (o.base_value * o.vat / Decimal('100')))
    date = datetime_date(2023, 1, 15)
    state = InvoiceStates.DRAFT

    @classmethod
    def build_invoice(cls, **kwargs):
        """
        Build and return an InvoiceModel instance without saving it to the database.
        :param kwargs: Optional fields to override (e.g., number, supplier, date, etc.).
        """
        # Ensure date is a datetime.date object, not a string
        if "date" in kwargs and isinstance(kwargs["date"], str):
            kwargs["date"] = datetime_date.fromisoformat(kwargs["date"])

        # Build the invoice instance with provided or default values
        invoice = cls.build(**kwargs)
        return invoice