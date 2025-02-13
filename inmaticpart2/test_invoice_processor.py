from decimal import Decimal
from django.test import TestCase
from inmaticpart2.invoice_processor import InvoiceProcessor
from inmaticpart2.accounting_codes import AccountingCodes
from inmaticpart2 import models
from inmaticpart2.payment_type import PaymentType  # Assuming the enums are imported from here

class InvoiceServiceTest(TestCase):

    def setUp(self):
        # Mock data: invoice numbers, dates, and amounts
        self.invoice_numbers = ["F2023/01", "F2023/02", "F2023/03"]
        self.invoice_dates = ["2023-01-15", "2023-01-17", "2023-01-18"]
        self.invoice_amounts = [121, 242, 363]

    def test_conversion_to_accounting_entry(self):
        # Create the InvoiceProcessor instance
        processor = InvoiceProcessor()

        # Call the method to process the invoices
        actual_result = processor.create_accounting_entries(self.invoice_numbers, self.invoice_dates, self.invoice_amounts)

        # Sort the invoices based on date for comparison
        sorted_invoices = sorted(self.invoice_numbers, key=lambda x: self.invoice_dates[self.invoice_numbers.index(x)])

        # Assert that invoices are sorted correctly
        self.assertEqual([invoice for invoice in actual_result["sorted_invoices"]], sorted_invoices)

        # Assert missing invoice numbers (F2023/42 in this case)
        self.assertEqual(actual_result["missing_invoice_numbers"], ["F2023/42"])

        # Assert no duplicate invoice numbers
        self.assertEqual(actual_result["duplicate_invoice_numbers"], [])

        # Assert the accounting entries are created correctly
        self.assertEqual(len(actual_result["accounting_entries"]), 9)  # 3 invoices * 3 entries per invoice

        # Assert the details of the accounting entries for each invoice
        # Checking the first invoice (F2023/01)
        entry = actual_result["accounting_entries"][0]
        self.assertEqual(entry.account_code.value, AccountingCodes.PURCHASES.value)
        self.assertEqual(entry.debit_credit.value, PaymentType.DEBIT.value)
        self.assertEqual(entry.amount, Decimal(121))
        self.assertEqual(entry.description, "Purchases for invoice F2023/01")
        self.assertEqual(entry.invoice_number, "F2023/01")

        # Checking the second entry for F2023/01 (VAT)
        entry = actual_result["accounting_entries"][1]
        self.assertEqual(entry.account_code.value, AccountingCodes.VAT_SUPPORTED.value)
        self.assertEqual(entry.debit_credit.value, PaymentType.DEBIT.value)
        self.assertEqual(entry.amount, Decimal(121) * Decimal(0.21))  # 21% of 121
        self.assertEqual(entry.description, "VAT for invoice F2023/01")
        self.assertEqual(entry.invoice_number, "F2023/01")

        # Checking the third entry for F2023/01 (Total)
        entry = actual_result["accounting_entries"][2]
        self.assertEqual(entry.account_code.value, AccountingCodes.SUPPLIERS.value)
        self.assertEqual(entry.debit_credit.value, PaymentType.CREDIT.value)
        self.assertEqual(entry.amount, Decimal(121) * Decimal(1.21))  # Total = 121 + VAT
        self.assertEqual(entry.description, "Total for invoice F2023/01")
        self.assertEqual(entry.invoice_number, "F2023/01")
