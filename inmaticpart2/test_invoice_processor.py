from decimal import Decimal
from django.test import TestCase
from datetime import date
from inmaticpart2.invoice_processor import InvoiceProcessor
from inmaticpart2.models import InvoiceModel

class InvoiceServiceTest(TestCase):

    def setUp(self):
        # Create test invoices with invoice numbers
        InvoiceModel.objects.create(
            number="F2023/01",  # Add this field
            provider="Provider A", 
            concept="Service 1", 
            base_value=Decimal("100.00"),
            vat=Decimal("21.00"),
            total_value=Decimal("121.00"),
            date=date(2023, 1, 15),
            state="DRAFT"
        )
        
        InvoiceModel.objects.create(
            number="F2023/02",  # Add this field
            provider="Provider B", 
            concept="Service 2", 
            base_value=Decimal("200.00"),
            vat=Decimal("42.00"),
            total_value=Decimal("242.00"),
            date=date(2023, 1, 17),
            state="DRAFT"
        )
        
        InvoiceModel.objects.create(
            number="F2023/03",  # Add this field
            provider="Provider C", 
            concept="Service 3", 
            base_value=Decimal("300.00"),
            vat=Decimal("63.00"),
            total_value=Decimal("363.00"),
            date=date(2023, 1, 18),
            state="DRAFT"
        )


    def test_conversion_to_accounting_entry(self):
        invoices = InvoiceModel.objects.all()

        # Call the method to process the invoices
        actualResult = InvoiceProcessor().convert_to_accounting_entry(invoices)

        print(actualResult)  # Debug output

        # Continue with the checks
        sorted_invoices = sorted(invoices, key=lambda x: x.date)
        self.assertEqual(
            [invoice.number for invoice in actualResult["sorted_invoices"]],
            [invoice.number for invoice in sorted_invoices]
        )

        self.assertEqual(actualResult["missing_invoice_numbers"], ["F2023/42"])
        self.assertEqual(actualResult["duplicate_invoice_numbers"], [])
