from typing import List, Dict
from datetime import date as datetime_date, datetime
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

        if start_date and end_date:
            self.invoice_builder.filter_by_date_range(start_date, end_date)

        if supplier_id:
            self.invoice_builder.filter_by_supplier(supplier_id)

        filtered_invoices = self.invoice_builder.apply_filters(invoices)
        sorted_invoices = self.invoice_builder.sort_invoices_by_date(filtered_invoices)

        if not isinstance(sorted_invoices, list):
            raise ValueError("Expected sorted_invoices to be a list of InvoiceModel objects.")

        self.validate_invoice_format([invoice.number for invoice in sorted_invoices])

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
    
    def cashflow_projection(start_date: datetime, end_date: datetime, invoices: List[InvoiceModel]):
        builder = InvoiceBuilder()
        builder.filter_by_date_range(start_date, end_date)
        filtered_invoices = builder.apply_filters(invoices)
        sorted_invoices = builder.sort_invoices_by_date(filtered_invoices)

        weekly_cashflow = {}
        monthly_cashflow = {}
        total_balance = Decimal('0.00')

        for invoice in sorted_invoices:
            week = invoice.date.strftime("%Y-%U")
            month = invoice.date.strftime("%Y-%m")

            if week not in weekly_cashflow:
                weekly_cashflow[week] = Decimal('0.00')
            weekly_cashflow[week] += invoice.total_value

            if month not in monthly_cashflow:
                monthly_cashflow[month] = Decimal('0.00')
            monthly_cashflow[month] += invoice.total_value

            total_balance += invoice.total_value

        return {
            "total_balance": total_balance,
            "weekly_cashflow": weekly_cashflow,
            "monthly_cashflow": monthly_cashflow,
        }