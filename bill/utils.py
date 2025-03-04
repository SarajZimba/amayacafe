from accounting.models import AccountLedger, TblCrJournalEntry, TblJournalEntry, TblDrJournalEntry, AccountChart, AccountSubLedger
from decimal import Decimal


def update_terminal_sub_ledger(terminal, branch, total, ledger):
    
    subled_name = f'{ledger.ledger_name} {branch}-{terminal}'
    try:
        sub = AccountSubLedger.objects.get(sub_ledger_name=subled_name)
        sub.total_value += Decimal(total)
        sub.save()

    except AccountSubLedger.DoesNotExist:
        AccountSubLedger.objects.create(sub_ledger_name=subled_name, total_value=total, is_editable=False, ledger=ledger)

def update_terminal_amount(terminal, branch, total):
    subled_name = f'Sales {branch}-{terminal}'
    sale_ledger = AccountLedger.objects.get(ledger_name='Sales')
    try:
        sub = AccountSubLedger.objects.get(sub_ledger_name=subled_name)
        sub.total_value += Decimal(total)
        sub.save()

    except AccountSubLedger.DoesNotExist:
        AccountSubLedger.objects.create(sub_ledger_name=subled_name, total_value=total, is_editable=False, ledger=sale_ledger)

def create_journal_for_complimentary(instance):
    grand_total = Decimal(instance.sub_total)
    complimentary_sales = AccountLedger.objects.get(ledger_name__iexact='complimentary sales')
    complimentary_expenses = AccountLedger.objects.get(ledger_name__iexact='complimentary expenses')

    journal_entry = TblJournalEntry.objects.create(employee_name='Created automatically during sale', journal_total=grand_total)
    TblDrJournalEntry.objects.create(particulars="Complimentary Expenses A/C Dr.", debit_amount = grand_total, journal_entry=journal_entry, ledger=complimentary_expenses)
    TblCrJournalEntry.objects.create(particulars="To Complimentary Sales", credit_amount = grand_total, journal_entry=journal_entry, ledger=complimentary_sales)
    
    complimentary_expenses.total_value += grand_total
    complimentary_expenses.save()

    complimentary_sales.total_value += grand_total
    complimentary_sales.save()


"""   :-(   """


def create_journal_for_bill(instance):
    payment_mode = instance.payment_mode.lower().strip()
    grand_total = Decimal(instance.grand_total)
    tax_amount = Decimal(instance.tax_amount)
    discount_amount = Decimal(instance.discount_amount)

    sale_ledger = AccountLedger.objects.get(ledger_name='Sales')
    journal_entry = TblJournalEntry.objects.create(employee_name='Created Automatically during Sale', journal_total=(grand_total-discount_amount))


    if discount_amount > 0:
        discount_expenses = AccountLedger.objects.get(ledger_name__iexact='Discount Expenses')
        discount_sales = AccountLedger.objects.get(ledger_name__iexact='Discount Sales')

        TblDrJournalEntry.objects.create(particulars="Discount Expenses A/C Dr.", debit_amount = discount_amount, journal_entry=journal_entry, ledger=discount_expenses)
        TblCrJournalEntry.objects.create(particulars="To Discount Sales", credit_amount = discount_amount, journal_entry=journal_entry, ledger=discount_sales)
        
        discount_expenses.total_value += discount_amount
        discount_expenses.save()

        discount_sales.total_value += discount_amount
        discount_sales.save()


    if tax_amount > 0:
        vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
        vat_payable.total_value = vat_payable.total_value + tax_amount
        vat_payable.save()
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To VAT Payable", ledger=vat_payable, credit_amount=tax_amount)

    if payment_mode == 'credit':
        account_chart = AccountChart.objects.get(group='Sundry Debtors')
        try:
            dr_ledger = AccountLedger.objects.get(ledger_name=f'{instance.customer.pk} - {instance.customer.name}')
            dr_ledger.total_value += grand_total
            dr_ledger.save()
        except AccountLedger.DoesNotExist:
            dr_ledger = AccountLedger.objects.create(ledger_name=f'{instance.customer.pk} - {instance.customer.name}', account_chart=account_chart, total_value=grand_total)

        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"{instance.customer.name} A/C Dr", ledger=dr_ledger, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))
        
        
    elif payment_mode == "credit card":
        card_transaction_ledger = AccountLedger.objects.get(ledger_name='Card Transactions')
        update_terminal_sub_ledger(terminal=instance.terminal, branch=instance.branch.branch_code, total=grand_total, ledger=card_transaction_ledger)
        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Card Transaction A/C Dr", ledger=card_transaction_ledger, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))
        card_transaction_ledger.total_value += grand_total
        card_transaction_ledger.save()


    elif payment_mode == "mobile payment":
        mobile_payment = AccountLedger.objects.get(ledger_name='Mobile Payments')
        update_terminal_sub_ledger(terminal=instance.terminal, branch=instance.branch.branch_code, total=grand_total, ledger=mobile_payment)

        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Mobile Payment A/C Dr", ledger=mobile_payment, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))
        mobile_payment.total_value += grand_total
        mobile_payment.save()


    elif payment_mode == "cash":
        cash_ledger = AccountLedger.objects.get(ledger_name='Cash-In-Hand')
        update_terminal_sub_ledger(terminal=instance.terminal, branch=instance.branch.branch_code, total=grand_total, ledger=cash_ledger)
        cash_ledger.total_value = cash_ledger.total_value + grand_total
        cash_ledger.save()

        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Cash A/C Dr", ledger=cash_ledger, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))

    sale_ledger.total_value += (grand_total-tax_amount)
    sale_ledger.save()


def create_split_payment_accounting(payment, total, branch, terminal, tax_amount, customer, discount):
    discount_amount = Decimal(discount)
    sale_ledger = AccountLedger.objects.get(ledger_name='Sales')
    sale_ledger.total_value = sale_ledger.total_value+Decimal(total-tax_amount)
    sale_ledger.save()
    
    journal = TblJournalEntry.objects.create(employee_name='Created Automatically during Sale', journal_total=total)
    TblCrJournalEntry.objects.create(journal_entry=journal, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(total-tax_amount))
    if tax_amount > 0:
        vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
        vat_payable.total_value = vat_payable.total_value + Decimal(tax_amount)
        vat_payable.save()
        TblCrJournalEntry.objects.create(journal_entry=journal, particulars=f"To VAT Payable", ledger=vat_payable, credit_amount=tax_amount)
    if discount_amount > 0:
        discount_expenses = AccountLedger.objects.get(ledger_name__iexact='Discount Expenses')
        TblDrJournalEntry.objects.create(particulars="Discount Expenses A/C Dr.", debit_amount = discount_amount, journal_entry=journal, ledger=discount_expenses)
        discount_expenses.total_value += discount_amount
        discount_expenses.save()


    for pay in payment:
        pay_amount = Decimal(pay.get('amount'))
        if pay['payment_mode'].lower().strip() == "cash":
            cash_ledger = AccountLedger.objects.get(ledger_name='Cash-In-Hand')
            update_terminal_sub_ledger(terminal=terminal, branch=branch, total= pay_amount, ledger=cash_ledger)
            cash_ledger.total_value = cash_ledger.total_value + pay_amount
            cash_ledger.save()
            TblDrJournalEntry.objects.create(journal_entry=journal, particulars=f"Cash A/C Dr", ledger=cash_ledger, debit_amount=pay_amount)

        elif pay['payment_mode'].lower().strip() == "mobile payment":
            mobile_payment = AccountLedger.objects.get(ledger_name='Mobile Payments')
            update_terminal_sub_ledger(terminal=terminal, branch=branch, total= pay_amount, ledger=mobile_payment)
            mobile_payment.total_value += pay_amount
            mobile_payment.save()
            TblDrJournalEntry.objects.create(journal_entry=journal, particulars=f"Mobile Payment A/C Dr", ledger=mobile_payment, debit_amount=pay_amount)
        
        elif pay['payment_mode'].lower().strip() == "credit card":
            card_transaction_ledger = AccountLedger.objects.get(ledger_name='Card Transactions')
            update_terminal_sub_ledger(terminal=terminal, branch=branch, total= pay_amount, ledger=card_transaction_ledger)
            TblDrJournalEntry.objects.create(journal_entry=journal, particulars=f"Card Transaction A/C Dr", ledger=card_transaction_ledger, debit_amount=pay_amount)
            card_transaction_ledger.total_value += pay_amount
            card_transaction_ledger.save()

        elif pay['payment_mode'].lower().strip() == "credit": 
            account_chart = AccountChart.objects.get(group='Sundry Debtors')
            try:
                dr_ledger = AccountLedger.objects.get(ledger_name=f'{customer.pk} - {customer.name}')
                dr_ledger.total_value += pay_amount
                dr_ledger.save()
            except AccountLedger.DoesNotExist:
                dr_ledger = AccountLedger.objects.create(ledger_name=f'{customer.pk} - {customer.name}', account_chart=account_chart, total_value=pay_amount)
            TblDrJournalEntry.objects.create(journal_entry=journal, particulars=f"{customer.name} A/C Dr", ledger=dr_ledger, debit_amount=pay_amount)



def reverse_accounting(instance):
    from bill.models import Bill
    bills = Bill.objects.filter(invoice_number=instance.bill_no, transaction_date=instance.bill_date)
    bill = bills.first() if bills else None
    if bill:
        branch_and_terminal = f"{bill.branch.branch_code}-{bill.terminal}"
        payment_mode = bill.payment_mode.lower().strip()
        grand_total = Decimal(bill.grand_total)
        tax_amount = Decimal(bill.tax_amount)
        discount_amount = Decimal(bill.discount_amount)

        sale_ledger = AccountLedger.objects.get(ledger_name='Sales')
        sale_terminal_subledger = AccountSubLedger.objects.get(sub_ledger_name__iexact=f"Sales {branch_and_terminal}")
        journal = TblJournalEntry.objects.create(employee_name="Created automatically during sales return", journal_total=grand_total)
        TblDrJournalEntry.objects.create(ledger=sale_ledger, particulars="Sales A\c DR", debit_amount=(grand_total-tax_amount), journal_entry=journal)

        if tax_amount > 0:
            vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
            vat_payable.total_value -= tax_amount
            vat_payable.save()
            TblDrJournalEntry.objects.create(ledger=vat_payable, particulars="Vat payable A\c Dr", debit_amount=tax_amount, journal_entry=journal)
        
        if discount_amount > 0:
            dis_sales = AccountLedger.objects.get(ledger_name='Discount Sales')
            dis_exp = AccountLedger.objects.get(ledger_name='Discount Expenses')
            dis_sales.total_value -= discount_amount
            dis_sales.save()
            dis_exp.total_value -= discount_amount
            dis_exp.save()

        if payment_mode == "cash":
            cash_ledger = AccountLedger.objects.get(ledger_name='Cash-In-Hand')
            cash_ledger.total_value -= grand_total
            cash_ledger.save()
            cash_terminal_subledger = AccountSubLedger.objects.get(sub_ledger_name__iexact=f'Cash-In-Hand {branch_and_terminal}')
            cash_terminal_subledger.total_value -= grand_total
            cash_terminal_subledger.save()
            TblCrJournalEntry.objects.create(ledger=cash_ledger, particulars="To Cash A\c", credit_amount=grand_total, journal_entry=journal)

        elif payment_mode == "mobile payment":
            mobile_payment_ledger = AccountLedger.objects.get(ledger_name__iexact='Mobile Payments')
            mobile_payment_ledger.total_value -= grand_total
            mobile_payment_ledger.save()
            mobile_payment_subledger = AccountSubLedger.objects.get(sub_ledger_name__iexact=f'Mobile Payments {branch_and_terminal}')
            mobile_payment_subledger.total_value -= grand_total
            mobile_payment_subledger.save()
            TblCrJournalEntry.objects.create(ledger=mobile_payment_ledger, particulars="To Mobile Payments A\c", credit_amount=grand_total, journal_entry=journal)

        if payment_mode == "credit card":
            card_ledger = AccountLedger.objects.get(ledger_name='Card Transactions')
            card_ledger.total_value -= grand_total
            card_ledger.save()
            card_terminal_subledger = AccountSubLedger.objects.get(sub_ledger_name__iexact=f'Card Transactions {branch_and_terminal}')
            card_terminal_subledger.total_value -= grand_total
            card_terminal_subledger.save()
            TblCrJournalEntry.objects.create(ledger=card_ledger, particulars="To Card Transactions A\c", credit_amount=grand_total, journal_entry=journal)

        sale_terminal_subledger.total_value -= (grand_total-tax_amount)
        sale_terminal_subledger.save()

        sale_ledger.total_value -= (grand_total-tax_amount)
        sale_ledger.save()

            




        


    