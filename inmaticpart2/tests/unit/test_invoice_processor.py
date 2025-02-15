from decimal import Decimal
from django.test import TestCase
from inmaticpart2.app.service.invoice_processor import InvoiceProcessor
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from datetime import date
from inmaticpart2.database.factories.invoice_factory import InvoiceModelFactory


class InvoiceServiceTest(TestCase):

    def setUp(self):
        invoice = InvoiceModelFactory

        self.invoice1 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(1)
            | invoice.generate_provider("Iberdrola")
            | invoice.generate_concept("Electricidad - Consumo enero 2023")
            | invoice.generate_base_value(Decimal("100.00"))
            | invoice.generate_vat(Decimal("21.00"))
            | invoice.generate_total_value(Decimal("121.00"))
            | invoice.generate_date(date(2023, 1, 15))
            | invoice.generate_state(InvoiceStates.ACCOUNTED))
        )

        self.invoice2 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(2)
            | invoice.generate_provider("Telefónica")
            | invoice.generate_concept("Servicios de telefonía fija y móvil")
            | invoice.generate_base_value(Decimal("200.00"))
            | invoice.generate_vat(Decimal("42.00"))
            | invoice.generate_total_value(Decimal("242.00"))
            | invoice.generate_date(date(2023, 1, 17))
            | invoice.generate_state(InvoiceStates.PAID))
        )

        self.invoice3 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(3)
            | invoice.generate_provider("Endesa")
            | invoice.generate_concept("Gas Natural - Consumo enero 2023")
            | invoice.generate_base_value(Decimal("300.00"))
            | invoice.generate_vat(Decimal("63.00"))
            | invoice.generate_total_value(Decimal("363.00"))
            | invoice.generate_date(date(2023, 1, 18))
            | invoice.generate_state(InvoiceStates.CANCELED))
        )


    def test_missing_invoice_number(self):
        # Testing that the "missing_invoice_numbers" functionality works.
        invoices = [self.invoice1, self.invoice2, self.invoice3]
        actual_result = InvoiceProcessor().create_accounting_entries(invoices)

        self.assertIn("F2023/04", actual_result["missing_invoice_numbers"])
        self.assertEqual(len(actual_result["missing_invoice_numbers"]), 39)
        self.assertEqual(
            actual_result["missing_invoice_numbers"][:5],
            ["F2023/04", "F2023/05", "F2023/06", "F2023/07", "F2023/08"]
        )

    def test_invoice_number_format(self):
        # Testing the validation of invoice number formats.
        valid_invoice_numbers = [self.invoice1.number, self.invoice2.number, self.invoice3.number]
        invoiceProcessor = InvoiceProcessor()

        invoiceProcessor.validate_invoice_format(valid_invoice_numbers)

        with self.assertRaises(ValueError):
            invoiceProcessor.validate_invoice_format(["F2023/01", "2023-02-03", "F2023/03"])

    def test_sort_invoices_by_date(self):
        # Testing that invoices are sorted by date correctly.
        invoices = [self.invoice1, self.invoice2, self.invoice3]
        sorted_result = InvoiceProcessor().sort_invoices_by_date(invoices)

        sorted_invoice_numbers = [invoice.number for invoice in sorted_result]
        expected_result = [self.invoice1.number, self.invoice2.number, self.invoice3.number]
        self.assertEqual(sorted_invoice_numbers, expected_result)

    def test_group_invoices_by_supplier_and_month(self):
        # Testing grouping of invoices by supplier and month.
        invoices = [self.invoice1, self.invoice2, self.invoice3]
        transition_result = InvoiceProcessor().group_invoices_by_supplier_and_month(invoices, InvoiceStates.PAID)

        # Ensure the "Telefónica" provider is in the results.
        self.assertIn("Telefónica", transition_result)

        # Check if invoices are grouped by month (2023-01 in this case).
        self.assertIn("2023-01", transition_result["Telefónica"])

        # Verify the base and VAT amounts for the group.
        self.assertEqual(transition_result["Telefónica"]["2023-01"]["base"], Decimal("200.00"))
        self.assertEqual(transition_result["Telefónica"]["2023-01"]["vat"], Decimal("42.00"))
