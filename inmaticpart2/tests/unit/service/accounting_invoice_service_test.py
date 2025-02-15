from decimal import Decimal
from datetime import datetime
from django.test import TestCase
from inmaticpart2.app.service.accounting_invoice_service import AccountingInvoiceService
from inmaticpart2.database.factories.invoice_factory import InvoiceModelFactory


class AccountingInvoiceServiceTest(TestCase):

    def setUp(self):
        self.invoice1 = InvoiceModelFactory.build_invoice(number="F2023/01", date=datetime(2023, 1, 15).date())
        self.invoice2 = InvoiceModelFactory.build_invoice(number="F2023/02", date=datetime(2023, 1, 20).date())
        self.invoice3 = InvoiceModelFactory.build_invoice(number="F2023/03", date=datetime(2023, 2, 10).date())

    def test_it_correctly_checks_for_missing_invoice_numbers(self):

        # Arrange
        invoices = [self.invoice1, self.invoice2, self.invoice3]
        
        # Act
        actual_result = AccountingInvoiceService().create_accounting_entries(invoices)

        # Assert
        self.assertIn("F2023/04", actual_result["missing_invoice_numbers"])
        self.assertEqual(len(actual_result["missing_invoice_numbers"]), 37)
        self.assertEqual(
            actual_result["missing_invoice_numbers"][:5],
            ["F2023/04", "F2023/05", "F2023/06", "F2023/07", "F2023/08"]
        )

    def test_it_correctly_validates_invoice_number_format(self):

        # Arrange
        valid_invoice_numbers = [self.invoice1.number, self.invoice2.number, self.invoice3.number]
        invoice_processor = AccountingInvoiceService()

        # Act
        invoice_processor.validate_invoice_format(valid_invoice_numbers)

        # Assert
        with self.assertRaises(ValueError):
            invoice_processor.validate_invoice_format(["F2023/01", "2023-02-03", "F2023/03"])

    def test_it_correctly_sorts_invoices_by_date(self):

        # Arrange
        invoices = [self.invoice3, self.invoice1, self.invoice2]
        invoice_processor = AccountingInvoiceService()
        
        # Act
        sorted_invoices = invoice_processor.invoice_builder.sort_invoices_by_date(invoices)

        # Assert
        sorted_invoice_numbers = [invoice.number for invoice in sorted_invoices]
        expected_result = [self.invoice1.number, self.invoice2.number, self.invoice3.number]
        self.assertEqual(sorted_invoice_numbers, expected_result)

    def test_it_raises_value_error_for_invalid_invoice_amount(self):

        # Arrange
        self.invoice1.total_value = Decimal("-100.00")
        invoice_processor = AccountingInvoiceService()

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            invoice_processor.create_accounting_entries([self.invoice1])

        self.assertEqual(str(context.exception), f"Invoice {self.invoice1.number} with amount -100.00 is not valid.")

    def test_it_detects_duplicate_invoice_numbers(self):

        # Arrange
        invoices = [self.invoice1, self.invoice1, self.invoice3]
        invoice_processor = AccountingInvoiceService()

        # Act
        duplicate_invoice_numbers = invoice_processor.invoice_builder.detect_duplicate_invoice_numbers(invoices)

        # Assert
        self.assertIn(self.invoice1.number, duplicate_invoice_numbers)
        self.assertEqual(len(duplicate_invoice_numbers), 1)

    def test_it_correctly_groups_invoices_by_supplier_and_month(self):
        
        # Arrange
        invoices = [self.invoice1, self.invoice2, self.invoice3]
        invoice_processor = AccountingInvoiceService()

        # Act
        grouped_invoices = invoice_processor.group_invoices_by_supplier_and_month(invoices)

        # Assert
        self.assertIn(self.invoice1.supplier, grouped_invoices)
        self.assertIn(self.invoice1.date.strftime('%Y-%m'), grouped_invoices[self.invoice1.supplier])
        self.assertEqual(len(grouped_invoices[self.invoice1.supplier][self.invoice1.date.strftime('%Y-%m')]["invoices"]), 2)
        self.assertEqual(len(grouped_invoices[self.invoice3.supplier][self.invoice3.date.strftime('%Y-%m')]["invoices"]), 1)
