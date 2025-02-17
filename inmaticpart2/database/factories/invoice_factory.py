import factory
from decimal import Decimal
from datetime import date as datetime_date
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from inmaticpart2.models import InvoiceModel


from datetime import timedelta

class InvoiceModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvoiceModel

    number = factory.Sequence(lambda n: f"F2023/{n + 1:02d}")
    supplier = "Telefónica"
    concept = "Sample concept for invoice."
    base_value = Decimal('100.00')
    vat = Decimal('21.00')
    total_value = factory.LazyAttribute(lambda o: o.base_value + (o.base_value * o.vat / Decimal('100')))
    date = datetime_date(2023, 1, 15)
    due_date = factory.LazyAttribute(lambda o: o.date + timedelta(days=30))  
    state = InvoiceStates.PENDING

    @classmethod
    def build_invoice(cls, **kwargs):
        if "date" in kwargs and isinstance(kwargs["date"], str):
            kwargs["date"] = datetime_date.fromisoformat(kwargs["date"])

        if "due_date" not in kwargs and "date" in kwargs:
            kwargs["due_date"] = kwargs["date"] + timedelta(days=30)  
        invoice = cls.build(**kwargs)
        return invoice
