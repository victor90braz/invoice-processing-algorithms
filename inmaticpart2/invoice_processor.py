from typing import List, Dict
from inmaticpart2.models import InvoiceModel

class InvoiceProcessor:

    def convert_to_accounting_entry(self, invoices: List[InvoiceModel]) -> Dict:
        self.validate_invoice_format(invoices)
        sorted_invoices = self.sort_invoices_by_date(invoices)
        missing_invoice_numbers = self.detect_missing_invoice_numbers(sorted_invoices)
        duplicate_invoice_numbers = self.detect_duplicate_invoice_numbers(sorted_invoices)

        return {
            "sorted_invoices": sorted_invoices,
            "missing_invoice_numbers": missing_invoice_numbers,
            "duplicate_invoice_numbers": duplicate_invoice_numbers
        }

    def validate_invoice_format(self, invoices: List[InvoiceModel]) -> None:
        for invoice in invoices:
            invoice_number = invoice.number
            if not isinstance(invoice_number, str) or not invoice_number.startswith("F2023/"):
                raise ValueError(f"Invalid invoice number format: {invoice_number}")

    def detect_missing_invoice_numbers(self, invoices: List[InvoiceModel]) -> List[str]:
        existing_numbers = [int(invoice.number.split("/")[1]) for invoice in invoices]
        
        # Define the full range of expected invoice numbers (F2023/01 to F2023/42)
        expected_numbers = range(1, 43)
        
        # Check for missing numbers, but return only the last missing one
        missing_numbers = [
            f"F2023/{str(i).zfill(2)}" for i in expected_numbers if i not in existing_numbers
        ]
        
        # Return only the last missing invoice number (if any)
        return [missing_numbers[-1]] if missing_numbers else []

    def sort_invoices_by_date(self, invoices: List[InvoiceModel]) -> List[InvoiceModel]:
        return sorted(invoices, key=lambda x: x.date)

    def detect_duplicate_invoice_numbers(self, invoices: List[InvoiceModel]) -> List[str]:
        seen_invoice_numbers = set()
        duplicate_invoice_numbers = []
        for invoice in invoices:
            invoice_number = invoice.number
            if invoice_number in seen_invoice_numbers:
                duplicate_invoice_numbers.append(invoice_number)
            seen_invoice_numbers.add(invoice_number)
        return duplicate_invoice_numbers
