from decimal import Decimal
from django.test import TestCase
from inmaticpart2.app.service.invoice_processor import InvoiceProcessor
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from inmaticpart2.database.factories.invoice_factory import InvoiceModelFactory


class InvoiceServiceTest(TestCase):

    def setUp(self):
        # Create sample invoices using the factory
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
        # Ensure invoices have the correct 'provider' and 'state'
        self.invoice1.provider = "Telefónica"
        self.invoice2.provider = "Telefónica"
        self.invoice3.provider = "Telefónica"
        
        self.invoice1.state = InvoiceStates.DRAFT
        self.invoice2.state = InvoiceStates.DRAFT
        self.invoice3.state = InvoiceStates.DRAFT

        # Now group by supplier and month
        invoice_processor = InvoiceProcessor()
        grouped_invoices = invoice_processor.group_invoices_by_supplier_and_month(
            [self.invoice1, self.invoice2, self.invoice3],
            InvoiceStates.DRAFT
        )
        
        # Check that 'Telefónica' is in the grouped invoices
        self.assertIn("Telefónica", grouped_invoices)
