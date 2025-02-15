from decimal import Decimal
from django.test import TestCase
from inmaticpart2.app.service.invoice_processor import InvoiceProcessor
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from inmaticpart2.database.factories.invoice_factory import InvoiceModelFactory


class InvoiceServiceTest(TestCase):

    def setUp(self):
        self.invoice1 = InvoiceModelFactory.build_invoice()
        self.invoice2 = InvoiceModelFactory.build_invoice()
        self.invoice3 = InvoiceModelFactory.build_invoice()

    def test_it_corrects_check_for_missing_invoice_numbers(self):
        invoices = [self.invoice1, self.invoice2, self.invoice3]
        actual_result = InvoiceProcessor().create_accounting_entries(invoices)

        self.assertIn("F2023/04", actual_result["missing_invoice_numbers"])
        self.assertEqual(len(actual_result["missing_invoice_numbers"]), 39)
        self.assertEqual(
            actual_result["missing_invoice_numbers"][:5],
            ["F2023/04", "F2023/05", "F2023/06", "F2023/07", "F2023/08"]
        )

    def test_it_corrects_validate_invoice_number_format(self):
        valid_invoice_numbers = [self.invoice1.number, self.invoice2.number, self.invoice3.number]
        invoiceProcessor = InvoiceProcessor()

        invoiceProcessor.validate_invoice_format(valid_invoice_numbers)

        with self.assertRaises(ValueError):
            invoiceProcessor.validate_invoice_format(["F2023/01", "2023-02-03", "F2023/03"])

    def test_it_corrects_sort_invoices_by_date(self):
        invoices = [self.invoice1, self.invoice2, self.invoice3]
        sorted_result = InvoiceProcessor().sort_invoices_by_date(invoices)

        sorted_invoice_numbers = [invoice.number for invoice in sorted_result]
        expected_result = [self.invoice1.number, self.invoice2.number, self.invoice3.number]
        self.assertEqual(sorted_invoice_numbers, expected_result)

    def test_it_corrects_group_invoices_by_supplier_and_month(self):
        self.invoice1.provider = "Telefónica"
        self.invoice2.provider = "Telefónica"
        self.invoice3.provider = "Telefónica"
        
        self.invoice1.state = InvoiceStates.DRAFT
        self.invoice2.state = InvoiceStates.DRAFT
        self.invoice3.state = InvoiceStates.DRAFT

        invoice_processor = InvoiceProcessor()
        grouped_invoices = invoice_processor.group_invoices_by_supplier_and_month(
            [self.invoice1, self.invoice2, self.invoice3],
            InvoiceStates.DRAFT
        )
        
        self.assertIn("Telefónica", grouped_invoices)

    def test_it_raises_value_error_for_invalid_invoice_amount(self):
        self.invoice1.total_value = Decimal("-100.00")
        
        invoice_processor = InvoiceProcessor()

        with self.assertRaises(ValueError) as context:
            invoice_processor.create_accounting_entries_for_invoices([self.invoice1])

        self.assertEqual(str(context.exception), f"Invoice {self.invoice1.number} with amount -100.00 is not valid.")

    def test_it_detects_duplicate_invoice_numbers(self):
        
        invoices = [self.invoice1, self.invoice1, self.invoice3]

        invoice_processor = InvoiceProcessor()

        duplicate_invoice_numbers = invoice_processor.detect_duplicate_invoice_numbers(invoices)

        self.assertIn(self.invoice1.number, duplicate_invoice_numbers)
        self.assertEqual(len(duplicate_invoice_numbers), 1)
