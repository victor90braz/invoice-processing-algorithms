from decimal import Decimal
from django.test import TestCase
from inmaticpart2.invoice_processor import InvoiceProcessor
from inmaticpart2.accounting_codes import AccountingCodes
from inmaticpart2 import models
from inmaticpart2.payment_type import PaymentType

class InvoiceServiceTest(TestCase):

    def setUp(self):

        self.invoiceProcessor = InvoiceProcessor()

        models.InvoiceModel.objects.create(
            number="F2023/01",
            provider="Provider A",
            concept="Service 1",
            base_value=Decimal("100.00"),
            vat=Decimal("21.00"),
            total_value=Decimal("121.00"),
            date="2023-01-15",
            state="DRAFT"
        )
        
        models.InvoiceModel.objects.create(
            number="F2023/02",
            provider="Provider B",
            concept="Service 2",
            base_value=Decimal("200.00"),
            vat=Decimal("42.00"),
            total_value=Decimal("242.00"),
            date="2023-01-17",
            state="DRAFT"
        )
        
        models.InvoiceModel.objects.create(
            number="F2023/03",
            provider="Provider C",
            concept="Service 3",
            base_value=Decimal("300.00"),
            vat=Decimal("63.00"),
            total_value=Decimal("363.00"),
            date="2023-01-18",
            state="DRAFT"
        )

    def test_missing_invoice_number(self):

        invoices = models.InvoiceModel.objects.all()
        actual_result = self.invoiceProcessor.create_accounting_entries(
            invoices
        )
        self.assertEqual(actual_result["missing_invoice_numbers"], ["F2023/42"])

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

        duplicate_invoices = list(duplicate_invoices) + [duplicate_invoices[0]]
        actual_result = self.invoiceProcessor.detect_duplicate_invoice_numbers(duplicate_invoices)
        self.assertEqual(actual_result, ["F2023/01"])
