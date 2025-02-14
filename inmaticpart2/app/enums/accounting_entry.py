from decimal import Decimal
from inmaticpart2.app.enums.accounting_codes import AccountingCodes  
from dataclasses import dataclass

from inmaticpart2.app.enums.payment_type import PaymentType

@dataclass
class AccountingEntry:
    account_code: AccountingCodes 
    debit_credit: PaymentType  
    amount: Decimal
    description: str
    invoice_number: str

    def __post_init__(self):

        if not isinstance(self.debit_credit, PaymentType ):
            raise ValueError(f"Invalid debit/credit value: {self.debit_credit}")
        
        if not isinstance(self.account_code, AccountingCodes):
            raise ValueError(f"Invalid account code: {self.account_code}")

    def __str__(self):
        return f"{self.debit_credit.value} {self.account_code.value}: {self.amount} - {self.description} ({self.invoice_number})"
