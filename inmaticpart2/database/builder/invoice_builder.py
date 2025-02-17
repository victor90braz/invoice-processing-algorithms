from datetime import date as datetime
from typing import List
from inmaticpart2.models import InvoiceModel


from typing import List
from datetime import datetime

class InvoiceBuilder:
    def __init__(self):
        self.filters = []

    def filter_by_date_range(self, start_date: datetime, end_date: datetime):
        self.filters.append(lambda invoice: start_date <= invoice.date <= end_date)

    def filter_by_supplier(self, supplier_id: int):
        self.filters.append(lambda invoice: invoice.supplier_id == supplier_id)

    def apply_filters(self, invoices: List[InvoiceModel]) -> List[InvoiceModel]:
        for filter_fn in self.filters:
            invoices = [invoice for invoice in invoices if filter_fn(invoice)]
        return invoices

    def sort_invoices_by_date(self, invoices: List[InvoiceModel]) -> List[InvoiceModel]:
        return sorted(invoices, key=lambda invoice: invoice.date)

    def detect_duplicate_invoice_numbers(self, invoices: List[InvoiceModel]) -> List[str]:
        seen = set()
        duplicates = []
        for invoice in invoices:
            if invoice.number in seen:
                duplicates.append(invoice.number)
            else:
                seen.add(invoice.number)
        return duplicates
