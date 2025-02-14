import factory
from decimal import Decimal
from datetime import date
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from inmaticpart2.models import InvoiceModel

class InvoiceModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvoiceModel

    @staticmethod
    def generate_invoice_number(n):
        return {"number": f"F2023/{n:02d}"}

    @staticmethod
    def generate_provider(provider="MyCompany Ltd."):
        return {"provider": provider}

    @staticmethod
    def generate_concept(concept="Sample concept for invoice."):
        return {"concept": concept}

    @staticmethod
    def generate_base_value(base_value=Decimal('100.00')):
        return {"base_value": base_value}

    @staticmethod
    def generate_vat(vat=Decimal('21.00')):
        return {"vat": vat}

    @staticmethod
    def generate_total_value(total_value=Decimal('121.00')):
        return {"total_value": total_value}

    @staticmethod
    def generate_date(invoice_date=date(2023, 1, 15)):
        return {"date": invoice_date}

    @staticmethod
    def generate_state(state=InvoiceStates.DRAFT):
        return {"state": state}
