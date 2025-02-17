from datetime import date as datetime
from typing import List
from inmaticpart2.models import InvoiceModel


class InvoiceBuilder:
    def __init__(self):
        self.filters = []

    def filter_by_date_range(self, start_date: datetime, end_date: datetime):
        print(f"Filtrando facturas entre {start_date} y {end_date}")
        self.filters.append(lambda invoice: start_date <= invoice.date <= end_date)

    def filter_by_supplier(self, supplier_id: int):
        self.filters.append(lambda invoice: invoice.supplier_id == supplier_id)

    def sort_invoices_by_date(self, invoices: List[InvoiceModel]) -> List[InvoiceModel]:
        return sorted(invoices, key=lambda invoice: invoice.date)

    def detect_duplicate_invoice_numbers(self, invoices: List[InvoiceModel]) -> List[str]:
        invoice_numbers = [invoice.number for invoice in invoices]
        duplicates = set([number for number in invoice_numbers if invoice_numbers.count(number) > 1])
        return list(duplicates)

    def filter_by_date_range(self, start_date: datetime, end_date: datetime):
        self.filters.append(lambda invoice: start_date <= invoice.date <= end_date)

    def apply_filters(self, invoices: List[InvoiceModel]) -> List[InvoiceModel]:
        filtered_invoices = invoices
        for filter_func in self.filters:
            filtered_invoices = list(filter(filter_func, filtered_invoices))
        return filtered_invoices

    def sort_invoices_by_date(self, invoices: List[InvoiceModel]) -> List[InvoiceModel]:
        return sorted(invoices, key=lambda invoice: invoice.date)
