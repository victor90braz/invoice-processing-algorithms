from typing import List, Dict
from datetime import date as datetime_date, datetime, timedelta
from decimal import Decimal
from collections import defaultdict
from inmaticpart2.database.builder.invoice_builder import InvoiceBuilder
from inmaticpart2.models import InvoiceModel


class AccountingInvoiceService:
    def __init__(self):
        self.invoice_builder = InvoiceBuilder()

    def create_accounting_entries(
        self,
        invoices: List[InvoiceModel],
        start_date: datetime_date = None,
        end_date: datetime_date = None,
        supplier_id: int = None
    ) -> Dict:
        for invoice in invoices:
            if invoice.total_value < Decimal("0.00"):
                raise ValueError(f"Invoice {invoice.number} with amount {invoice.total_value} is not valid.")

        # Apply filters based on provided parameters
        if start_date and end_date:
            self.invoice_builder.filter_by_date_range(start_date, end_date)
        if supplier_id:
            self.invoice_builder.filter_by_supplier(supplier_id)

        # Apply filters and sort invoices
        filtered_invoices = self.invoice_builder.apply_filters(invoices)
        sorted_invoices = self.invoice_builder.sort_invoices_by_date(filtered_invoices)

        if not isinstance(sorted_invoices, list):
            raise ValueError("Expected sorted_invoices to be a list of InvoiceModel objects.")

        self.validate_invoice_format([invoice.number for invoice in sorted_invoices])

        # Group, process invoices, and return results
        grouped_invoices = self.group_invoices_by_supplier_and_month(sorted_invoices)
        accounting_entries = self.process_grouped_invoices(grouped_invoices)

        missing_invoice_numbers = self.find_missing_invoice_numbers(sorted_invoices)
        duplicate_invoice_numbers = self.invoice_builder.detect_duplicate_invoice_numbers(sorted_invoices)

        return {
            "grouped_invoices": grouped_invoices,
            "missing_invoice_numbers": missing_invoice_numbers,
            "duplicate_invoice_numbers": duplicate_invoice_numbers,
            "accounting_entries": accounting_entries,
        }

    def group_invoices_by_supplier_and_month(self, invoices: List[InvoiceModel]) -> Dict:
        grouped_invoices = defaultdict(lambda: defaultdict(lambda: {"total_base": Decimal("0.00"), "total_value": Decimal("0.00"), "invoices": []}))

        for invoice in invoices:
            supplier = invoice.supplier
            month = invoice.date.strftime("%Y-%m")

            grouped_invoices[supplier][month]["invoices"].append(invoice)
            grouped_invoices[supplier][month]["total_base"] += invoice.base_value
            grouped_invoices[supplier][month]["total_value"] += invoice.total_value

        return grouped_invoices

    def validate_invoice_format(self, invoice_numbers: List[str]) -> None:
        for invoice_number in invoice_numbers:
            if not invoice_number.startswith("F"):
                raise ValueError(f"Invalid invoice number format: {invoice_number}")

    def find_missing_invoice_numbers(self, invoices: List[InvoiceModel]) -> List[str]:
        all_invoice_numbers = [invoice.number for invoice in invoices]
        expected_invoice_numbers = self.generate_expected_invoice_numbers()
        return [number for number in expected_invoice_numbers if number not in all_invoice_numbers]

    def generate_expected_invoice_numbers(self) -> List[str]:
        return [f"F2023/{str(i).zfill(2)}" for i in range(1, 41)]

    def process_grouped_invoices(self, grouped_invoices: Dict) -> List[Dict]:
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

    def cashflow_projection(self, start_date: datetime, end_date: datetime, invoices: List[InvoiceModel]):
        start_date = start_date  # Convert to date
        end_date = end_date  # Convert to date

        # First, apply filters based on the date range and other parameters
        if start_date and end_date:
            self.invoice_builder.filter_by_date_range(start_date, end_date)

        # Apply filters and sort invoices
        filtered_invoices = self.invoice_builder.apply_filters(invoices)
        
        # Debug: Log the filtered invoices
        print(f"Filtered invoices (after applying filters): {filtered_invoices}")

        sorted_invoices = self.invoice_builder.sort_invoices_by_date(filtered_invoices)

        # Initialize variables to accumulate the projections
        total_balance = sum(invoice.total_value for invoice in sorted_invoices)

        weekly_cashflow = defaultdict(Decimal)
        monthly_cashflow = defaultdict(Decimal)

        # Calculate monthly cashflow projections
        for invoice in sorted_invoices:
            # Group by month for monthly cashflow
            month_str = invoice.date.strftime("%Y-%m")  # Get the month as YYYY-MM format
            monthly_cashflow[month_str] += invoice.total_value

            # Calculate weekly cashflow (if necessary)
            week_start = invoice.date - timedelta(days=invoice.date.weekday())  # Get the start of the week
            weekly_cashflow[week_start.strftime("%Y-%m-%d")] += invoice.total_value

        # Debug: Log the total balance and cashflow projections
        print(f"Total Balance: {total_balance}")
        print(f"Weekly Cashflow: {dict(weekly_cashflow)}")
        print(f"Monthly Cashflow: {dict(monthly_cashflow)}")

        # Return the result with monthly cashflow and weekly cashflow if needed
        return {
            "total_balance": total_balance,
            "weekly_cashflow": dict(weekly_cashflow),  # Grouped by week
            "monthly_cashflow": dict(monthly_cashflow),  # Grouped by month
        }
