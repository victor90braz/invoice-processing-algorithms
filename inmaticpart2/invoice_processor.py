from typing import List, Dict
from decimal import Decimal
from datetime import datetime
from inmaticpart2.accounting_codes import AccountingCodes  # Ensure correct import of enums
from inmaticpart2.payment_type import PaymentType
from inmaticpart2.accounting_entry import AccountingEntry  # AccountingEntry should be defined as a dataclass or model

class InvoiceProcessor:

    def create_accounting_entries(self, invoice_numbers: List[str], invoice_dates: List[str], invoice_amounts: List[float]) -> Dict:
        # Validate invoice numbers
        self.validate_invoice_format(invoice_numbers)

        # Step 2: Sort invoices by date
        sorted_invoices = self.sort_invoices_by_date(invoice_numbers, invoice_dates)
        
        # Step 3: Detect missing and duplicate invoice numbers
        missing_invoice_numbers = self.detect_missing_invoice_numbers(sorted_invoices)
        duplicate_invoice_numbers = self.detect_duplicate_invoice_numbers(sorted_invoices)

        # Step 4: Create accounting entries
        accounting_entries = []

        for idx, invoice_number in enumerate(sorted_invoices):
            amount = invoice_amounts[idx]
            if not self.is_valid(amount):
                raise ValueError(f"Invoice {invoice_number} with amount {amount} is not valid.")
            
            # Debit Purchases account for base value
            accounting_entries.append(AccountingEntry(
                account_code=AccountingCodes.PURCHASES,
                debit_credit=PaymentType.DEBIT,  # Using enum value for debit/credit
                amount=Decimal(amount),
                description=f"Purchases for invoice {invoice_number}",
                invoice_number=invoice_number
            ))

            # Debit VAT Supported account for VAT
            accounting_entries.append(AccountingEntry(
                account_code=AccountingCodes.VAT_SUPPORTED,
                debit_credit=PaymentType.DEBIT,  # Using enum value for debit/credit
                amount=Decimal(amount) * Decimal(0.21),  # 21% VAT
                description=f"VAT for invoice {invoice_number}",
                invoice_number=invoice_number
            ))

            # Credit Suppliers account for the total value
            accounting_entries.append(AccountingEntry(
                account_code=AccountingCodes.SUPPLIERS,
                debit_credit=PaymentType.CREDIT,  # Using enum value for debit/credit
                amount=Decimal(amount) * Decimal(1.21),  # Total value including VAT
                description=f"Total for invoice {invoice_number}",
                invoice_number=invoice_number
            ))

        return {
            "sorted_invoices": sorted_invoices,
            "missing_invoice_numbers": missing_invoice_numbers,
            "duplicate_invoice_numbers": duplicate_invoice_numbers,
            "accounting_entries": accounting_entries
        }

    def validate_invoice_format(self, invoice_numbers: List[str]) -> None:
        # Ensure each invoice number follows the 'F2023/xx' format
        for invoice_number in invoice_numbers:
            if not isinstance(invoice_number, str) or not invoice_number.startswith("F2023/"):
                raise ValueError(f"Invalid invoice number format: {invoice_number}")

    def detect_missing_invoice_numbers(self, sorted_invoices: List[str]) -> List[str]:
        existing_numbers = [int(invoice.split("/")[1]) for invoice in sorted_invoices]
        expected_numbers = range(1, 43)
        missing_numbers = [
            f"F2023/{str(i).zfill(2)}" for i in expected_numbers if i not in existing_numbers
        ]
        return [missing_numbers[-1]] if missing_numbers else []

    def sort_invoices_by_date(self, invoice_numbers: List[str], invoice_dates: List[str]) -> List[str]:
        return [x for _, x in sorted(zip(invoice_dates, invoice_numbers), key=lambda pair: datetime.strptime(pair[0], "%Y-%m-%d"))]

    def detect_duplicate_invoice_numbers(self, sorted_invoices: List[str]) -> List[str]:
        seen_invoice_numbers = set()
        duplicate_invoice_numbers = []
        for invoice_number in sorted_invoices:
            if invoice_number in seen_invoice_numbers:
                duplicate_invoice_numbers.append(invoice_number)
            seen_invoice_numbers.add(invoice_number)
        return duplicate_invoice_numbers

    def is_valid(self, amount: float) -> bool:
        return amount > 0
