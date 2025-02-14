from decimal import Decimal
from django.test import TestCase
from inmaticpart2.app.service.invoice_processor import InvoiceProcessor
from inmaticpart2.app.enums.accounting_codes import AccountingCodes
from inmaticpart2.app.enums.payment_type import PaymentType
from inmaticpart2.app.enums.invoice_states import InvoiceStates
from datetime import date

from inmaticpart2.database.factories.invoice_factory import InvoiceModelFactory


class InvoiceServiceTest(TestCase):

    def test_missing_invoice_number(self):

        # Arrange
        invoice1 = InvoiceModelFactory(number="F2023/01", provider="Iberdrola", concept="Electricidad - Consumo enero 2023", base_value=Decimal("100.00"), vat=Decimal("21.00"), total_value=Decimal("121.00"), date=date(2023, 1, 15), state=InvoiceStates.ACCOUNTED)
        invoice2 = InvoiceModelFactory(number="F2023/02", provider="Telefónica", concept="Servicios de telefonía fija y móvil", base_value=Decimal("200.00"), vat=Decimal("42.00"), total_value=Decimal("242.00"), date=date(2023, 1, 17), state=InvoiceStates.PAID)
        invoice3 = InvoiceModelFactory(number="F2023/03", provider="Endesa", concept="Gas Natural - Consumo enero 2023", base_value=Decimal("300.00"), vat=Decimal("63.00"), total_value=Decimal("363.00"), date=date(2023, 1, 18), state=InvoiceStates.CANCELED)
        invoices = [invoice1, invoice2, invoice3]

        invoiceProcessor = InvoiceProcessor()

        # Act
        actual_result = invoiceProcessor.create_accounting_entries(invoices)

        # Assert
        self.assertIn("F2023/42", actual_result["missing_invoice_numbers"])
        self.assertEqual(len(actual_result["missing_invoice_numbers"]), 39)
        self.assertEqual(
            actual_result["missing_invoice_numbers"][:5],
            ["F2023/04", "F2023/05", "F2023/06", "F2023/07", "F2023/08"]
        )

    def test_invoice_number_format(self):

        # Arrange
        invoice1 = InvoiceModelFactory(number="F2023/01", provider="Iberdrola", concept="Electricidad - Consumo enero 2023", base_value=Decimal("100.00"), vat=Decimal("21.00"), total_value=Decimal("121.00"), date=date(2023, 1, 15), state=InvoiceStates.ACCOUNTED)
        invoice2 = InvoiceModelFactory(number="F2023/02", provider="Telefónica", concept="Servicios de telefonía fija y móvil", base_value=Decimal("200.00"), vat=Decimal("42.00"), total_value=Decimal("242.00"), date=date(2023, 1, 17), state=InvoiceStates.PAID)
        invoice3 = InvoiceModelFactory(number="F2023/03", provider="Endesa", concept="Gas Natural - Consumo enero 2023", base_value=Decimal("300.00"), vat=Decimal("63.00"), total_value=Decimal("363.00"), date=date(2023, 1, 18), state=InvoiceStates.CANCELED)
        valid_invoice_numbers = [invoice1.number, invoice2.number, invoice3.number]

        invoiceProcessor = InvoiceProcessor()

        # Act
        invoiceProcessor.validate_invoice_format(valid_invoice_numbers)

        # Assert
        with self.assertRaises(ValueError):
            invoiceProcessor.validate_invoice_format(["F2023/01", "2023-02-03", "F2023/03"])

    def test_sort_invoices_by_date(self):

        # Arrange
        invoice1 = InvoiceModelFactory(date=date(2023, 1, 15))
        invoice2 = InvoiceModelFactory(date=date(2023, 1, 17))
        invoice3 = InvoiceModelFactory(date=date(2023, 1, 18))
        invoices = [invoice1, invoice2, invoice3]

        invoiceProcessor = InvoiceProcessor()

        # Act
        sorted_result = invoiceProcessor.sort_invoices_by_date(invoices)

        # Assert
        sorted_invoice_numbers = [invoice.number for invoice in sorted_result]
        expected_result = [invoice1.number, invoice2.number, invoice3.number]
        self.assertEqual(sorted_invoice_numbers, expected_result)

    def test_duplicate_invoice_detection(self):

        # Arrange
        invoice1 = InvoiceModelFactory()
        invoice2 = InvoiceModelFactory()
        invoice3 = InvoiceModelFactory()
        duplicate_invoices = [invoice1, invoice1, invoice2, invoice3]

        invoiceProcessor = InvoiceProcessor()

        # Act
        actual_result = invoiceProcessor.detect_duplicate_invoice_numbers(duplicate_invoices)

        # Assert
        self.assertEqual(actual_result, [invoice1.number])

    def test_accounting_entries_with_enums(self):

        # Arrange
        invoice1 = InvoiceModelFactory(base_value=Decimal("100.00"), vat=Decimal("21.00"), total_value=Decimal("121.00"))
        invoice2 = InvoiceModelFactory(base_value=Decimal("200.00"), vat=Decimal("42.00"), total_value=Decimal("242.00"))
        invoice3 = InvoiceModelFactory(base_value=Decimal("300.00"), vat=Decimal("63.00"), total_value=Decimal("363.00"))
        invoices = [invoice1, invoice2, invoice3]

        invoiceProcessor = InvoiceProcessor()

        # Act
        actual_result = invoiceProcessor.create_accounting_entries(invoices)
        accounting_entries = actual_result["accounting_entries"]

        # Assert
        self.assertIn("sorted_invoices", actual_result)
        self.assertIn("missing_invoice_numbers", actual_result)
        self.assertIn("duplicate_invoice_numbers", actual_result)
        self.assertIn("accounting_entries", actual_result)

        entry = accounting_entries[0]
        self.assertEqual(entry.account_code, AccountingCodes.PURCHASES)
        self.assertEqual(entry.debit_credit, PaymentType.DEBIT)

        entry = accounting_entries[1]
        self.assertEqual(entry.account_code, AccountingCodes.VAT_SUPPORTED)
        self.assertEqual(entry.debit_credit, PaymentType.DEBIT)

        entry = accounting_entries[2]
        self.assertEqual(entry.account_code, AccountingCodes.SUPPLIERS)
        self.assertEqual(entry.debit_credit, PaymentType.CREDIT)

    def test_group_invoices_by_supplier_and_month(self):
        
        # Arrange
        invoice1 = InvoiceModelFactory(provider="Iberdrola", date=date(2023, 1, 10))
        invoice2 = InvoiceModelFactory(provider="Iberdrola", date=date(2023, 1, 15))
        invoice3 = InvoiceModelFactory(provider="Iberdrola", date=date(2023, 1, 20))
        invoice4 = InvoiceModelFactory(provider="Telefónica", date=date(2023, 2, 15), base_value=Decimal("100.00"))
        invoice5 = InvoiceModelFactory(provider="Telefónica", date=date(2023, 2, 15), base_value=Decimal("100.00"))
        invoices = [invoice1, invoice2, invoice3, invoice4, invoice5]

        invoiceProcessor = InvoiceProcessor()

        # Act
        grouped_invoices = invoiceProcessor.group_invoices_by_supplier_and_month(invoices)

        # Assert
        # Iberdrola
        supplier_iber = grouped_invoices["Iberdrola"]
        self.assertEqual(len(supplier_iber["2023-01"]["invoices"]), 3)
        self.assertEqual(supplier_iber["2023-01"]["base"], Decimal("300.00"))
        self.assertEqual(supplier_iber["2023-01"]["vat"], Decimal("63.00"))

        # Telefónica
        supplier_tel = grouped_invoices["Telefónica"]
        self.assertEqual(len(supplier_tel["2023-02"]["invoices"]), 2)
        self.assertEqual(supplier_tel["2023-02"]["base"], Decimal("200.00"))
        self.assertEqual(supplier_tel["2023-02"]["vat"], Decimal("42.00"))
