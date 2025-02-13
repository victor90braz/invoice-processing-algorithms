from decimal import Decimal
from django.test import TestCase
from inmaticpart2.invoice_processor import InvoiceProcessor
from inmaticpart2.accounting_codes import AccountingCodes
from inmaticpart2 import models
from inmaticpart2.payment_type import PaymentType
from inmaticpart2.invoice_states import InvoiceStates
from datetime import date

class InvoiceServiceTest(TestCase):

    def setUp(self):
        # Initialize InvoiceProcessor as an instance
        self.invoiceProcessor = InvoiceProcessor()

        # Create InvoiceModel instances with correct date format
        models.InvoiceModel.objects.create(
            number="F2023/01",
            provider="Provider A",
            concept="Service 1",
            base_value=Decimal("100.00"),
            vat=Decimal("21.00"),
            total_value=Decimal("121.00"),
            date=date(2023, 1, 15),  # Correct date format (not a string)
            state=InvoiceStates.ACCOUNTED
        )
        
        models.InvoiceModel.objects.create(
            number="F2023/02",
            provider="Provider B",
            concept="Service 2",
            base_value=Decimal("200.00"),
            vat=Decimal("42.00"),
            total_value=Decimal("242.00"),
            date=date(2023, 1, 17),
            state=InvoiceStates.PAID
        )
        
        models.InvoiceModel.objects.create(
            number="F2023/03",
            provider="Provider C",
            concept="Service 3",
            base_value=Decimal("300.00"),
            vat=Decimal("63.00"),
            total_value=Decimal("363.00"),
            date=date(2023, 1, 18),
            state=InvoiceStates.CANCELED
        )

    def test_missing_invoice_number(self):
        invoices = models.InvoiceModel.objects.all()
        actual_result = self.invoiceProcessor.create_accounting_entries(invoices)

        # Check that 'F2023/42' is in the missing invoice numbers
        self.assertIn("F2023/42", actual_result["missing_invoice_numbers"])

        # Check the total number of missing invoices
        self.assertEqual(len(actual_result["missing_invoice_numbers"]), 39)

        # Optionally, check that the first few missing invoices are correctly returned
        self.assertEqual(actual_result["missing_invoice_numbers"][:5], 
                        ["F2023/04", "F2023/05", "F2023/06", "F2023/07", "F2023/08"])

    def test_invoice_number_format(self):
        valid_invoice_numbers = ["F2023/01", "F2023/02", "F2023/03"]
        self.invoiceProcessor.validate_invoice_format(valid_invoice_numbers)

        with self.assertRaises(ValueError):
            self.invoiceProcessor.validate_invoice_format(["F2023/01", "2023-02-03", "F2023/03"])

    def test_sort_invoices_by_date(self):
        invoices = models.InvoiceModel.objects.all()
        sorted_result = self.invoiceProcessor.sort_invoices_by_date(invoices)
        
        sorted_invoice_numbers = [invoice.number for invoice in sorted_result]
        
        expected_result = ["F2023/01", "F2023/02", "F2023/03"]
        
        self.assertEqual(sorted_invoice_numbers, expected_result)

    def test_duplicate_invoice_detection(self):
        duplicate_invoices = models.InvoiceModel.objects.all()

        # Add a duplicate invoice
        duplicate_invoices = list(duplicate_invoices) + [duplicate_invoices[0]]
        actual_result = self.invoiceProcessor.detect_duplicate_invoice_numbers(duplicate_invoices)
        self.assertEqual(actual_result, ["F2023/01"])

    def test_accounting_entries_with_enums(self):
        invoices = models.InvoiceModel.objects.all()
        actual_result = self.invoiceProcessor.create_accounting_entries(invoices)
        
        accounting_entries = actual_result["accounting_entries"]

        # Check entries for the first invoice
        entry = accounting_entries[0]
        self.assertEqual(entry.account_code, AccountingCodes.PURCHASES)
        self.assertEqual(entry.debit_credit, PaymentType.DEBIT)

        entry = accounting_entries[1]
        self.assertEqual(entry.account_code, AccountingCodes.VAT_SUPPORTED)
        self.assertEqual(entry.debit_credit, PaymentType.DEBIT)

        entry = accounting_entries[2]
        self.assertEqual(entry.account_code, AccountingCodes.SUPPLIERS)
        self.assertEqual(entry.debit_credit, PaymentType.CREDIT)
