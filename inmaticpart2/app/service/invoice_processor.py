from collections import defaultdict
from typing import List, Dict
from decimal import Decimal
from inmaticpart2.app.enums.accounting_codes import AccountingCodes
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from inmaticpart2.app.enums.payment_type import PaymentType
from inmaticpart2.app.dtos.accounting_entry import AccountingEntry
from inmaticpart2.models import InvoiceModel
import re


class InvoiceProcessor:

    def create_accounting_entries(self, invoices: List[InvoiceModel]) -> Dict:

        self.validate_invoice_format([invoice.number for invoice in invoices])

        sorted_invoices = self.sort_invoices_by_date(invoices)

        return {
            "sorted_invoices": sorted_invoices,
            "missing_invoice_numbers": self.detect_missing_invoice_numbers(sorted_invoices),
            "duplicate_invoice_numbers": self.detect_duplicate_invoice_numbers(sorted_invoices),
            "accounting_entries": self.create_accounting_entries_for_invoices(sorted_invoices)
        }

    def create_accounting_entries_for_invoices(self, sorted_invoices: List[InvoiceModel]) -> List[AccountingEntry]:
        accounting_entries = []

        for invoice in sorted_invoices:
            amount = invoice.total_value
            if not self.is_valid(amount):
                raise ValueError(f"Invoice {invoice.number} with amount {amount} is not valid.")
            
            accounting_entries.extend([
                AccountingEntry(
                    account_code=AccountingCodes.PURCHASES,
                    debit_credit=PaymentType.DEBIT,
                    amount=Decimal(invoice.base_value),
                    description=f"Purchases for invoice {invoice.number}",
                    invoice_number=invoice.number
                ),
                AccountingEntry(
                    account_code=AccountingCodes.VAT_SUPPORTED,
                    debit_credit=PaymentType.DEBIT,
                    amount=Decimal(invoice.vat),
                    description=f"VAT for invoice {invoice.number}",
                    invoice_number=invoice.number
                ),
                AccountingEntry(
                    account_code=AccountingCodes.SUPPLIERS,
                    debit_credit=PaymentType.CREDIT,
                    amount=Decimal(invoice.total_value),
                    description=f"Total for invoice {invoice.number}",
                    invoice_number=invoice.number
                )
            ])

        return accounting_entries

    def validate_invoice_format(self, invoice_numbers: List[str]) -> None:
        pattern = r"^F\d{4}/\d{2}$"
        for invoice_number in invoice_numbers:
            if not re.match(pattern, invoice_number):
                raise ValueError(f"Invalid invoice number format: {invoice_number}")

    def detect_missing_invoice_numbers(self, sorted_invoices: List[InvoiceModel]) -> List[str]:
        existing_invoice_numbers = [int(invoice.number.split("/")[1]) for invoice in sorted_invoices]

        total_invoice_count_for_year = 42
        expected_invoice_numbers = range(1, total_invoice_count_for_year + 1)

        missing_invoice_numbers = [
            f"F2023/{str(expected_number).zfill(2)}" for expected_number in expected_invoice_numbers 
            if expected_number not in existing_invoice_numbers
        ]

        return missing_invoice_numbers

    def sort_invoices_by_date(self, invoices: List[InvoiceModel]) -> List[InvoiceModel]:
        return sorted(invoices, key=lambda invoice: invoice.date)

    def detect_duplicate_invoice_numbers(self, sorted_invoices: List[InvoiceModel]) -> List[str]:
        seen_invoice_numbers = set()
        duplicate_invoice_numbers = []
        for invoice in sorted_invoices:
            if invoice.number in seen_invoice_numbers:
                duplicate_invoice_numbers.append(invoice.number)
            seen_invoice_numbers.add(invoice.number)
        return duplicate_invoice_numbers

    def is_valid(self, amount: float) -> bool:
        return amount > 0

    def group_invoices_by_supplier_and_month(self, invoices: List[InvoiceModel], state: InvoiceStates) -> Dict:
        grouped_invoices = defaultdict(lambda: defaultdict(lambda: {"base": Decimal(0), "vat": Decimal(0), "invoices": []}))

        # Filter invoices by state
        invoices = [invoice for invoice in invoices if invoice.state == state]

        for invoice in invoices:
            supplier = invoice.provider
            month = invoice.date.strftime('%Y-%m')

            # Add base and VAT to the corresponding supplier and month
            grouped_invoices[supplier][month]["base"] += Decimal(invoice.base_value)
            grouped_invoices[supplier][month]["vat"] += Decimal(invoice.vat)
            grouped_invoices[supplier][month]["invoices"].append(invoice)

        # Sort invoices by date within each group (supplier and month)
        for supplier, months in grouped_invoices.items():
            for month, data in months.items():
                # Sort invoices by date within the group
                data["invoices"].sort(key=lambda invoice: invoice.date)

        return grouped_invoices