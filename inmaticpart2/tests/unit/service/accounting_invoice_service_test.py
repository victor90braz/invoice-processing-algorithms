from decimal import Decimal
from datetime import date, datetime
from unittest.mock import patch
from django.test import TestCase
from inmaticpart2.app.service.accounting_invoice_service import AccountingInvoiceService
from inmaticpart2.database.factories.invoice_factory import InvoiceModelFactory


class AccountingInvoiceServiceTest(TestCase):

    def setUp(self):
        self.invoice1 = InvoiceModelFactory.build_invoice(
            number="F2023/01",
            date=datetime(2023, 1, 15).date(),
            supplier="Telefónica"
        )
        self.invoice2 = InvoiceModelFactory.build_invoice(
            number="F2023/02",
            date=datetime(2023, 1, 20).date(),
            supplier="Telefónica"
        )
        self.invoice3 = InvoiceModelFactory.build_invoice(
            number="F2023/03",
            date=datetime(2023, 2, 10).date(),
            supplier="Telefónica"
        )
        self.invoice4 = InvoiceModelFactory.build_invoice(
            number="F2023/04",
            date=datetime(2023, 1, 15).date(),
            supplier="Vodafone"
        )

    def test_it_calls_filter_by_date_range_when_start_date_and_end_date_are_provided(self):
        # Arrange
        start_date = datetime(2023, 1, 1).date()
        end_date = datetime(2023, 1, 31).date()
        invoices = [self.invoice1, self.invoice2, self.invoice3]
        invoice_processor = AccountingInvoiceService()

        # Act
        with patch.object(invoice_processor.invoice_builder, 'filter_by_date_range') as mock_filter_by_date_range:
            invoice_processor.create_accounting_entries(invoices, start_date, end_date)

        # Assert
        mock_filter_by_date_range.assert_called_once_with(start_date, end_date)

    def test_it_calls_filter_by_supplier_when_supplier_id_is_provided(self):
        # Arrange
        supplier_id = 1
        invoices = [self.invoice1, self.invoice2, self.invoice3]
        invoice_processor = AccountingInvoiceService()

        # Act
        with patch.object(invoice_processor.invoice_builder, 'filter_by_supplier') as mock_filter_by_supplier:
            invoice_processor.create_accounting_entries(invoices, supplier_id=supplier_id)

        # Assert
        mock_filter_by_supplier.assert_called_once_with(supplier_id)

    def test_it_raises_value_error_if_sorted_invoices_is_not_a_list(self):
        # Arrange
        invoices = [self.invoice1, self.invoice2, self.invoice3]
        invoice_processor = AccountingInvoiceService()
        invoice_processor.invoice_builder.sort_invoices_by_date = lambda x: "not_a_list"  

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            invoice_processor.create_accounting_entries(invoices)

        self.assertEqual(str(context.exception), "Expected sorted_invoices to be a list of InvoiceModel objects.")

    def test_it_correctly_checks_for_missing_invoice_numbers(self):
        # Arrange
        invoices = [self.invoice1, self.invoice2, self.invoice3]

        # Act
        actual_result = AccountingInvoiceService().create_accounting_entries(invoices)

        # Assert
        missing_invoices = actual_result["missing_invoice_numbers"]

        self.assertEqual(len(missing_invoices), 37)
        self.assertListEqual(
            missing_invoices[:5],
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
        self.assertListEqual(sorted_invoice_numbers, [self.invoice1.number, self.invoice2.number, self.invoice3.number])

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
        invoices = [self.invoice1, self.invoice2, self.invoice3, self.invoice4]
        invoice_processor = AccountingInvoiceService()

        # Act
        grouped_invoices = invoice_processor.group_invoices_by_supplier_and_month(invoices)

        # Assert 
        self.assertIn("Telefónica", grouped_invoices)
        self.assertIn(self.invoice1.date.strftime('%Y-%m'), grouped_invoices["Telefónica"])
        self.assertEqual(len(grouped_invoices["Telefónica"][self.invoice1.date.strftime('%Y-%m')]["invoices"]), 2)

        actual_base_value_telef = self.invoice1.base_value + self.invoice2.base_value
        actual_total_value_telef = self.invoice1.total_value + self.invoice2.total_value

        self.assertEqual(grouped_invoices["Telefónica"][self.invoice1.date.strftime('%Y-%m')]["total_base"], actual_base_value_telef)
        self.assertEqual(grouped_invoices["Telefónica"][self.invoice1.date.strftime('%Y-%m')]["total_value"], actual_total_value_telef)

        self.assertIn("Vodafone", grouped_invoices)
        self.assertIn(self.invoice4.date.strftime('%Y-%m'), grouped_invoices["Vodafone"])
        self.assertEqual(len(grouped_invoices["Vodafone"][self.invoice4.date.strftime('%Y-%m')]["invoices"]), 1)
