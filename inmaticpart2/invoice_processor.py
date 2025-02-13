from typing import List, Dict
from decimal import Decimal
from inmaticpart2.accounting_codes import AccountingCodes
from inmaticpart2.payment_type import PaymentType
from inmaticpart2.accounting_entry import AccountingEntry
from inmaticpart2.models import InvoiceModel  # Import the model

class InvoiceProcessor:

    def create_accounting_entries(self, invoices: List[InvoiceModel]) -> Dict:
        # Validate invoice numbers
        self.validate_invoice_format([invoice.number for invoice in invoices])

        # Step 2: Sort invoices by date
        sorted_invoices = self.sort_invoices_by_date(invoices)
        
        # Step 3: Detect missing and duplicate invoice numbers
        missing_invoice_numbers = self.detect_missing_invoice_numbers(sorted_invoices)
        duplicate_invoice_numbers = self.detect_duplicate_invoice_numbers(sorted_invoices)

        # Step 4: Create accounting entries
        accounting_entries = []

        for invoice in sorted_invoices:
            # Access all the necessary details from the invoice model
            amount = invoice.total_value
            if not self.is_valid(amount):
                raise ValueError(f"Invoice {invoice.number} with amount {amount} is not valid.")
            
            # Debit Purchases account for base value
            accounting_entries.append(AccountingEntry(
                account_code=AccountingCodes.PURCHASES,
                debit_credit=PaymentType.DEBIT,
                amount=Decimal(invoice.base_value),
                description=f"Purchases for invoice {invoice.number}",
                invoice_number=invoice.number
            ))

            # Debit VAT Supported account for VAT
            accounting_entries.append(AccountingEntry(
                account_code=AccountingCodes.VAT_SUPPORTED,
                debit_credit=PaymentType.DEBIT,
                amount=Decimal(invoice.vat),
                description=f"VAT for invoice {invoice.number}",
                invoice_number=invoice.number
            ))

            # Credit Suppliers account for the total value
            accounting_entries.append(AccountingEntry(
                account_code=AccountingCodes.SUPPLIERS,
                debit_credit=PaymentType.CREDIT,
                amount=Decimal(invoice.total_value),
                description=f"Total for invoice {invoice.number}",
                invoice_number=invoice.number
            ))

        return {
            "sorted_invoices": sorted_invoices,
            "missing_invoice_numbers": missing_invoice_numbers,
            "duplicate_invoice_numbers": duplicate_invoice_numbers,
            "accounting_entries": accounting_entries
        }

    def validate_invoice_format(self, invoice_numbers: List[str]) -> None:
        for invoice_number in invoice_numbers:
            if not isinstance(invoice_number, str) or not invoice_number.startswith("F2023/"):
                raise ValueError(f"Invalid invoice number format: {invoice_number}")

    def detect_missing_invoice_numbers(self, sorted_invoices: List[InvoiceModel]) -> List[str]:
        existing_numbers = [int(invoice.number.split("/")[1]) for invoice in sorted_invoices]
        expected_numbers = range(1, 43)
        missing_numbers = [
            f"F2023/{str(i).zfill(2)}" for i in expected_numbers if i not in existing_numbers
        ]
        return [missing_numbers[-1]] if missing_numbers else []

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
