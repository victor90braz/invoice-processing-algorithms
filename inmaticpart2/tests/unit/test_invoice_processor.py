from decimal import Decimal
from django.test import TestCase
from inmaticpart2.app.service.invoice_processor import InvoiceProcessor
from inmaticpart2.app.enums.accounting_codes import AccountingCodes
from inmaticpart2.app.enums.payment_type import PaymentType
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from datetime import date

from inmaticpart2.database.factories.invoice_factory import InvoiceModelFactory


class InvoiceServiceTest(TestCase):

    def test_create_factory(self):
        invoice = InvoiceModelFactory

        # Chaining static methods to create the invoice data
        resultInvoice = (
            invoice.generate_invoice_number(1) |
            invoice.generate_provider("MyCompany Ltd.") |
            invoice.generate_concept("Sample concept for invoice.") |
            invoice.generate_base_value(Decimal('100.00')) |
            invoice.generate_vat(Decimal('21.00')) |
            invoice.generate_total_value(Decimal('121.00')) |
            invoice.generate_date(date(2023, 1, 15)) |
            invoice.generate_state(InvoiceStates.DRAFT)
        )

        self.assertEqual(resultInvoice, {
            "number": "F2023/01",
            "provider": "MyCompany Ltd.",
            "concept": "Sample concept for invoice.",
            "base_value": Decimal('100.00'),
            "vat": Decimal('21.00'),
            "total_value": Decimal('121.00'),
            "date": date(2023, 1, 15),
            "state": InvoiceStates.DRAFT
        })

    def test_missing_invoice_number(self):
        invoice = InvoiceModelFactory

        # Chaining static methods to create the invoice data
        invoice1 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(1) |
               invoice.generate_provider("Iberdrola") |
               invoice.generate_concept("Electricidad - Consumo enero 2023") |
               invoice.generate_base_value(Decimal("100.00")) |
               invoice.generate_vat(Decimal("21.00")) |
               invoice.generate_total_value(Decimal("121.00")) |
               invoice.generate_date(date(2023, 1, 15)) |
               invoice.generate_state(InvoiceStates.ACCOUNTED))
        )

        invoice2 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(2) |
               invoice.generate_provider("Telefónica") |
               invoice.generate_concept("Servicios de telefonía fija y móvil") |
               invoice.generate_base_value(Decimal("200.00")) |
               invoice.generate_vat(Decimal("42.00")) |
               invoice.generate_total_value(Decimal("242.00")) |
               invoice.generate_date(date(2023, 1, 17)) |
               invoice.generate_state(InvoiceStates.PAID))
        )

        invoice3 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(3) |
               invoice.generate_provider("Endesa") |
               invoice.generate_concept("Gas Natural - Consumo enero 2023") |
               invoice.generate_base_value(Decimal("300.00")) |
               invoice.generate_vat(Decimal("63.00")) |
               invoice.generate_total_value(Decimal("363.00")) |
               invoice.generate_date(date(2023, 1, 18)) |
               invoice.generate_state(InvoiceStates.CANCELED))
        )

        invoices = [invoice1, invoice2, invoice3]

        invoiceProcessor = InvoiceProcessor()

        # Act
        actual_result = invoiceProcessor.create_accounting_entries(invoices)

        # Assert
        self.assertIn("F2023/04", actual_result["missing_invoice_numbers"])
        self.assertEqual(len(actual_result["missing_invoice_numbers"]), 39)
        self.assertEqual(
            actual_result["missing_invoice_numbers"][:5],
            ["F2023/04", "F2023/05", "F2023/06", "F2023/07", "F2023/08"]
        )

    def test_invoice_number_format(self):
        invoice = InvoiceModelFactory

        # Chaining static methods to create the invoice data
        invoice1 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(1) |
               invoice.generate_provider("Iberdrola") |
               invoice.generate_concept("Electricidad - Consumo enero 2023") |
               invoice.generate_base_value(Decimal("100.00")) |
               invoice.generate_vat(Decimal("21.00")) |
               invoice.generate_total_value(Decimal("121.00")) |
               invoice.generate_date(date(2023, 1, 15)) |
               invoice.generate_state(InvoiceStates.ACCOUNTED))
        )

        invoice2 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(2) |
               invoice.generate_provider("Telefónica") |
               invoice.generate_concept("Servicios de telefonía fija y móvil") |
               invoice.generate_base_value(Decimal("200.00")) |
               invoice.generate_vat(Decimal("42.00")) |
               invoice.generate_total_value(Decimal("242.00")) |
               invoice.generate_date(date(2023, 1, 17)) |
               invoice.generate_state(InvoiceStates.PAID))
        )

        invoice3 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(3) |
               invoice.generate_provider("Endesa") |
               invoice.generate_concept("Gas Natural - Consumo enero 2023") |
               invoice.generate_base_value(Decimal("300.00")) |
               invoice.generate_vat(Decimal("63.00")) |
               invoice.generate_total_value(Decimal("363.00")) |
               invoice.generate_date(date(2023, 1, 18)) |
               invoice.generate_state(InvoiceStates.CANCELED))
        )

        valid_invoice_numbers = [invoice1.number, invoice2.number, invoice3.number]

        invoiceProcessor = InvoiceProcessor()

        # Act
        invoiceProcessor.validate_invoice_format(valid_invoice_numbers)

        # Assert
        with self.assertRaises(ValueError):
            invoiceProcessor.validate_invoice_format(["F2023/01", "2023-02-03", "F2023/03"])

    def test_sort_invoices_by_date(self):
        invoice = InvoiceModelFactory

        # Chaining static methods to create the invoice data
        invoice1 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(1) |
               invoice.generate_provider("Iberdrola") |
               invoice.generate_concept("Electricidad - Consumo enero 2023") |
               invoice.generate_base_value(Decimal("100.00")) |
               invoice.generate_vat(Decimal("21.00")) |
               invoice.generate_total_value(Decimal("121.00")) |
               invoice.generate_date(date(2023, 1, 15)) |
               invoice.generate_state(InvoiceStates.ACCOUNTED))
        )

        invoice2 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(2) |
               invoice.generate_provider("Telefónica") |
               invoice.generate_concept("Servicios de telefonía fija y móvil") |
               invoice.generate_base_value(Decimal("200.00")) |
               invoice.generate_vat(Decimal("42.00")) |
               invoice.generate_total_value(Decimal("242.00")) |
               invoice.generate_date(date(2023, 1, 17)) |
               invoice.generate_state(InvoiceStates.PAID))
        )

        invoice3 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(3) |
               invoice.generate_provider("Endesa") |
               invoice.generate_concept("Gas Natural - Consumo enero 2023") |
               invoice.generate_base_value(Decimal("300.00")) |
               invoice.generate_vat(Decimal("63.00")) |
               invoice.generate_total_value(Decimal("363.00")) |
               invoice.generate_date(date(2023, 1, 18)) |
               invoice.generate_state(InvoiceStates.CANCELED))
        )

        invoices = [invoice1, invoice2, invoice3]

        invoiceProcessor = InvoiceProcessor()

        # Act
        sorted_result = invoiceProcessor.sort_invoices_by_date(invoices)

        # Assert
        sorted_invoice_numbers = [invoice.number for invoice in sorted_result]
        expected_result = [invoice1.number, invoice2.number, invoice3.number]
        self.assertEqual(sorted_invoice_numbers, expected_result)

    def test_invoice_state_transition(self):
        invoice = InvoiceModelFactory

        # Chaining static methods to create the invoice data
        invoice1 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(1) |
            invoice.generate_provider("A") |
            invoice.generate_concept("Invoice for A - January 2023") |
            invoice.generate_base_value(Decimal("100.00")) |
            invoice.generate_vat(Decimal("21.00")) |
            invoice.generate_total_value(Decimal("121.00")) |
            invoice.generate_date(date(2023, 1, 15)) |
            invoice.generate_state(InvoiceStates.PAID))  # Ensure this is 'PAID'
        )

        invoice2 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(2) |
            invoice.generate_provider("A") |
            invoice.generate_concept("Invoice for A - January 2023") |
            invoice.generate_base_value(Decimal("200.00")) |
            invoice.generate_vat(Decimal("42.00")) |
            invoice.generate_total_value(Decimal("242.00")) |
            invoice.generate_date(date(2023, 1, 17)) |
            invoice.generate_state(InvoiceStates.PAID))  # Ensure this is 'PAID'
        )

        invoice3 = InvoiceModelFactory(
            **(invoice.generate_invoice_number(3) |
            invoice.generate_provider("B") |
            invoice.generate_concept("Invoice for B - January 2023") |
            invoice.generate_base_value(Decimal("300.00")) |
            invoice.generate_vat(Decimal("63.00")) |
            invoice.generate_total_value(Decimal("363.00")) |
            invoice.generate_date(date(2023, 1, 18)) |
            invoice.generate_state(InvoiceStates.PAID))  # Ensure this is 'PAID'
        )

        invoices = [invoice1, invoice2, invoice3]

        invoiceProcessor = InvoiceProcessor()

        # Act
        transition_result = invoiceProcessor.group_invoices_by_supplier_and_month(invoices, InvoiceStates.PAID)

        # Print invoices to debug
        print("Grouped invoices for 'A':", transition_result.get("A", {}))

        # Assert
        self.assertIn("A", transition_result)
        self.assertIn("2023-01", transition_result["A"])

        # Verifying that the base and VAT are correctly accumulated for 'A' in '2023-01'
        self.assertEqual(transition_result["A"]["2023-01"]["base"], Decimal("300.00"))  # 100.00 + 200.00
        self.assertEqual(transition_result["A"]["2023-01"]["vat"], Decimal("63.00"))   # 21.00 + 42.00
