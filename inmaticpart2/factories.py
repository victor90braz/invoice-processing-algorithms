import factory
from decimal import Decimal
from datetime import date
from inmaticpart2.invoice_states import InvoiceStates
from inmaticpart2.models import InvoiceModel

class InvoiceModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvoiceModel
    
    provider = factory.Faker('company')
    concept = factory.Faker('text')
    base_value = factory.LazyFunction(lambda: Decimal('100.00'))
    vat = factory.LazyFunction(lambda: Decimal('21.00'))
    total_value = factory.LazyFunction(lambda: Decimal('121.00'))
    date = factory.LazyFunction(lambda: date(2023, 1, 15))
    state = InvoiceStates.DRAFT
