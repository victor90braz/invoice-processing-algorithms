from collections import defaultdict
from decimal import Decimal
from datetime import datetime, timedelta
from inmaticpart2.app.dtos.accounting_entry import AccountingEntry
from inmaticpart2.app.enums.accounting_codes import AccountingCodes
from inmaticpart2.app.enums.payment_type import PaymentType
from inmaticpart2.database.builder.invoice_builder import InvoiceBuilder
from inmaticpart2.models import InvoiceModel
from typing import List


class AccountingInvoiceService:
    def __init__(self):
        self.invoice_builder = InvoiceBuilder()

    def create_accounting_entries(
        self,
        invoices: List[InvoiceModel],
        start_date: datetime = None,
        end_date: datetime = None,
        supplier_id: int = None
    ) -> dict:
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

    def group_invoices_by_supplier_and_month(self, invoices: List[InvoiceModel]) -> dict:
        grouped_invoices = defaultdict(lambda: defaultdict(lambda: {"total_base": Decimal("0.00"), "total_value": Decimal("0.00"), "invoices": []}))

        for invoice in invoices:
            supplier = invoice.supplier
            month = invoice.date.strftime("%Y-%m")

            grouped_invoices[supplier][month]["invoices"].append(invoice)
            grouped_invoices[supplier][month]["total_base"] += invoice.base_value
            grouped_invoices[supplier][month]["total_value"] += invoice.total_value

        return grouped_invoices

    def process_grouped_invoices(self, grouped_invoices: dict, account_code=None, debit_credit=None) -> list:
        accounting_entries = []

        account_code = account_code or AccountingCodes.PURCHASES
        debit_credit = debit_credit or PaymentType.DEBIT

        for supplier, months in grouped_invoices.items():
            for month, details in months.items():
                for invoice in details["invoices"]:
                    accounting_entries.append(AccountingEntry(
                        account_code=account_code,  
                        debit_credit=debit_credit,  
                        amount=invoice.total_value,
                        description=f"Invoice {invoice.number} for {month} from {supplier}",
                        invoice_number=invoice.number
                    ))

        return accounting_entries

    def validate_invoice_format(self, invoice_numbers: List[str]) -> None:
        for invoice_number in invoice_numbers:
            if not invoice_number.startswith("F"):
                raise ValueError(f"Invalid invoice number format: {invoice_number}")

    def find_missing_invoice_numbers(self, invoices: List[InvoiceModel]) -> list:
        all_invoice_numbers = [invoice.number for invoice in invoices]
        expected_invoice_numbers = self.generate_expected_invoice_numbers()
        return [number for number in expected_invoice_numbers if number not in all_invoice_numbers]

    def generate_expected_invoice_numbers(self) -> list:
        return [f"F2023/{str(i).zfill(2)}" for i in range(1, 41)]

    def cashflow_projection(self, start_date: datetime, end_date: datetime, invoices: List[InvoiceModel]) -> dict:
        filtered_invoices = [
            invoice for invoice in invoices
            if start_date <= invoice.date <= end_date
        ]

        filtered_invoices = self.invoice_builder.apply_filters(filtered_invoices)

        sorted_invoices = self.invoice_builder.sort_invoices_by_date(filtered_invoices)

        total_balance = sum(invoice.total_value for invoice in sorted_invoices)

        weekly_cashflow = defaultdict(Decimal)
        monthly_cashflow = defaultdict(Decimal)

        for invoice in sorted_invoices:
            month_str = invoice.date.strftime("%Y-%m")
            monthly_cashflow[month_str] += invoice.total_value

            week_start = invoice.date - timedelta(days=invoice.date.weekday())
            weekly_cashflow[week_start.strftime("%Y-%m-%d")] += invoice.total_value

        return {
            "total_balance": total_balance,
            "weekly_cashflow": dict(weekly_cashflow),
            "monthly_cashflow": dict(monthly_cashflow),
        }
