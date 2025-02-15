from typing import List, Dict
from datetime import datetime
from decimal import Decimal
from collections import defaultdict
from inmaticpart2.database.builder.invoice_builder import InvoiceBuilder
from inmaticpart2.models import InvoiceModel


class AccountingInvoiceService:
    def __init__(self):
        # Initialize necessary components such as InvoiceBuilder
        self.invoice_builder = InvoiceBuilder()

    def create_accounting_entries(
        self,
        invoices: List[InvoiceModel],
        start_date: datetime = None,
        end_date: datetime = None,
        supplier_id: int = None
    ) -> Dict:
        """
        Create accounting entries for the provided invoices with optional filters by date range and supplier.
        """
        # Validate invoice amounts
        for invoice in invoices:
            if invoice.total_value < Decimal("0.00"):
                raise ValueError(f"Invoice {invoice.number} with amount {invoice.total_value} is not valid.")

        # Apply date range and supplier filters using the InvoiceBuilder
        if start_date and end_date:
            self.invoice_builder.filter_by_date_range(start_date, end_date)

        if supplier_id:
            self.invoice_builder.filter_by_supplier(supplier_id)

        # Apply filters and retrieve the sorted invoices
        filtered_invoices = self.invoice_builder.apply_filters(invoices)
        sorted_invoices = self.invoice_builder.sort_invoices_by_date(filtered_invoices)

        # Ensure the filtered result is a list of InvoiceModel objects
        if not isinstance(sorted_invoices, list):
            raise ValueError("Expected sorted_invoices to be a list of InvoiceModel objects.")

        # Validate the invoice number format
        self.validate_invoice_format([invoice.number for invoice in sorted_invoices])

        # Group invoices by supplier and month
        grouped_invoices = self.group_invoices_by_supplier_and_month(sorted_invoices)

        # Process the grouped invoices to create accounting entries
        accounting_entries = self.process_grouped_invoices(grouped_invoices)

        # Find any missing invoice numbers
        missing_invoice_numbers = self.find_missing_invoice_numbers(sorted_invoices)

        # Detect duplicate invoice numbers
        duplicate_invoice_numbers = self.invoice_builder.detect_duplicate_invoice_numbers(sorted_invoices)

        # Return the result with grouped invoices, missing invoice numbers, and duplicates
        return {
            "grouped_invoices": grouped_invoices,
            "missing_invoice_numbers": missing_invoice_numbers,
            "duplicate_invoice_numbers": duplicate_invoice_numbers,
            "accounting_entries": accounting_entries,
        }

    def group_invoices_by_supplier_and_month(self, invoices: List[InvoiceModel]) -> Dict:
        """
        Group invoices by supplier and month, calculating total base and value for each group.
        """
        grouped_invoices = defaultdict(lambda: defaultdict(lambda: {"total_base": Decimal("0.00"), "total_value": Decimal("0.00"), "invoices": []}))

        for invoice in invoices:
            supplier = invoice.supplier
            month = invoice.date.strftime("%Y-%m")  # Format the month as "YYYY-MM"

            # Append the invoice to the respective group and update totals
            grouped_invoices[supplier][month]["invoices"].append(invoice)
            grouped_invoices[supplier][month]["total_base"] += invoice.base_value
            grouped_invoices[supplier][month]["total_value"] += invoice.total_value

        return grouped_invoices

    def validate_invoice_format(self, invoice_numbers: List[str]) -> None:
        """
        Validate that all invoice numbers are in the correct format.
        """
        for invoice_number in invoice_numbers:
            if not invoice_number.startswith("F"):
                raise ValueError(f"Invalid invoice number format: {invoice_number}")

    def find_missing_invoice_numbers(self, invoices: List[InvoiceModel]) -> List[str]:
        """
        Find any missing invoice numbers based on the expected sequence.
        """
        all_invoice_numbers = [invoice.number for invoice in invoices]
        expected_invoice_numbers = self.generate_expected_invoice_numbers()
        missing_invoice_numbers = [
            number for number in expected_invoice_numbers if number not in all_invoice_numbers
        ]
        return missing_invoice_numbers

    def generate_expected_invoice_numbers(self) -> List[str]:
        """
        Generate the expected invoice numbers (example logic).
        """
        return [f"F2023/{str(i).zfill(2)}" for i in range(1, 41)]  # Example: F2023/01, F2023/02, etc.

    def process_grouped_invoices(self, grouped_invoices: Dict) -> List[Dict]:
        """
        Process the grouped invoices and create accounting entries for each group.
        """
        accounting_entries = []

        for supplier, months in grouped_invoices.items():
            for month, details in months.items():
                accounting_entries.append({
                    "supplier": supplier,
                    "month": month,
                    "total_base": details["total_base"],
                    "total_value": details["total_value"],
                    "invoice_count": len(details["invoices"]),
                })

        return accounting_entries