from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView,DetailView,ListView,TemplateView,UpdateView,View
from root.utils import DeleteMixin
from .models import AccountChart, Depreciation, FiscalYearLedger, FiscalYearSubLedger, CumulativeLedger
from django.views.generic import TemplateView
from .forms import AccountChartForm
from decimal import Decimal as D
from django.db.models import Q, Sum
from django.contrib import messages
from organization.models import Organization
from rest_framework.response import Response
from accounting.utils import calculate_depreciation
from rest_framework.decorators import api_view
from user.permission import IsAdminOrAccountingMixin

class AccountChartMixin(IsAdminOrAccountingMixin):
    model = AccountChart
    form_class = AccountChartForm
    paginate_by = 10
    queryset = AccountChart.objects.prefetch_related('accountledger_set')
    success_url = reverse_lazy('accountchart_list')


class AccountChartList(AccountChartMixin, ListView):
    queryset = AccountChart.objects.all()
    template_name = "accounting/accounting_chart.html"


    def get(self, request, *args, **kwargs):
        query_set = self.queryset
        assets = query_set.filter(account_type='Asset')
        liabilities = query_set.filter(account_type='Liability')
        equities = query_set.filter(account_type='Equity')
        revenues = query_set.filter(account_type='Revenue')
        expenses = query_set.filter(account_type='Expense')
        others = query_set.filter(account_type='Other')


        context = {
            'assets': assets,
            'liabilities':liabilities,
            'equities':equities,
            'revenues':revenues,
            'expenses': expenses,
            'others': others
        }
        return render(request, 'accounting/accounting_chart.html', context)



class AccountChartDetail(AccountChartMixin, DetailView):
    template_name = "accounting/accountchart_detail.html"

class AccountChartCreate(AccountChartMixin, CreateView):
    template_name = "accounting/create.html"

class AccountChartUpdate(AccountChartMixin, UpdateView):
    template_name = "update.html"

class AccountChartDelete(AccountChartMixin, DeleteMixin, View):
    pass


from .models import AccountLedger
from .forms import AccountLedgerForm
class AccountLedgerMixin(IsAdminOrAccountingMixin):
    model = AccountLedger
    form_class = AccountLedgerForm
    paginate_by = 10
    queryset = AccountLedger.objects.all()
    success_url = reverse_lazy('accountledger_list')

class AccountLedgerList(AccountLedgerMixin, ListView):
    template_name = "accounting/accountledger_list.html"
    queryset = AccountLedger.objects.all()

class AccountLedgerDetail(AccountLedgerMixin, DetailView):
    template_name = "accounting/accountledger_detail.html"

class AccountLedgerCreate(AccountLedgerMixin, CreateView):
    template_name = "accounting/create.html"

class AccountLedgerUpdate(AccountLedgerMixin, UpdateView):
    template_name = "update.html"

class AccountLedgerDelete(AccountChartMixin, DeleteMixin, View):
    pass


from .forms import AccountSubLedgerForm
class AccountSubLedgerCreate(IsAdminOrAccountingMixin, CreateView):
    template_name = "accounting/subledger/create.html"
    form_class = AccountSubLedgerForm
    success_url = reverse_lazy('accountchart_list')

from .models import Expense
from .forms import ExpenseForm
class ExpenseMixin(IsAdminOrAccountingMixin):
    model = Expense
    form_class = ExpenseForm
    paginate_by = 10
    queryset = Expense.objects.all()
    success_url = reverse_lazy('expenses_list')

class ExpenseList(ExpenseMixin, ListView):
    template_name = "accounting/expenses/expenses_list.html"

class ExpenseDetail(ExpenseMixin, DetailView):
    template_name = "expense/expense_detail.html"

class ExpenseCreate(ExpenseMixin, CreateView):
    template_name = "accounting/expenses/expenses_create.html"

class ExpenseUpdate(ExpenseMixin, UpdateView):
    template_name = "update.html"

class ExpenseDelete(ExpenseMixin, DeleteMixin, View):
    pass



from .models import TblDrJournalEntry, TblCrJournalEntry, TblJournalEntry, AccountSubLedger

class JournalEntryCreateView(IsAdminOrAccountingMixin, View):

    def get(self, request):
        ledgers = AccountLedger.objects.all()
        sub_ledgers = AccountSubLedger.objects.all()
        return render(request, 'accounting/journal/journal_entry_create.html', {'ledgers':ledgers, 'sub_ledgers':sub_ledgers})
    
    def get_subledger(self, subledger, ledger):
        subled = None
        if not subledger.startswith('-'):
            try:
                subledger_id = int(subledger)
                subled = AccountSubLedger.objects.get(pk=subledger_id)
            except ValueError:
                subled = AccountSubLedger.objects.create(sub_ledger_name=subledger, is_editable=True, ledger=ledger)
        return subled
    
    def post(self, request):
        data = request.POST
        debit_ledgers = data.getlist('debit_ledger', [])
        debit_particulars = data.getlist('debit_particular', [])
        debit_amounts = data.getlist('debit_amount', [])
        debit_subledgers = data.getlist('debit_subledger', [])

        credit_ledgers = data.getlist('credit_ledger', [])
        credit_particulars = data.getlist('credit_particular', [])
        credit_amounts = data.getlist('credit_amount', [])
        credit_subledgers = data.getlist('credit_subledger', [])

        ledgers = AccountLedger.objects.all()
        sub_ledgers = AccountSubLedger.objects.all()

        try:
            parsed_debitamt = (lambda x: [D(i) for i in x])(debit_amounts)
            parsed_creditamt = (lambda x: [D(i) for i in x])(credit_amounts)
        except Exception:
            messages.error(request, "Please Enter valid amount")
            return render(request, 'accounting/journal/journal_entry_create.html', {'ledgers':ledgers, 'sub_ledgers':sub_ledgers})
        
        debit_sum, credit_sum = sum(parsed_debitamt), sum(parsed_creditamt)
        if debit_sum != credit_sum:
            messages.error(request, "Debit Total and Credit Total must be equal")
            return render(request, 'accounting/journal/journal_entry_create.html', {'ledgers':ledgers, 'sub_ledgers':sub_ledgers})

        for dr in debit_ledgers:
            if dr.startswith('-'):
                messages.error(request, "Ledger must be selected")
                return render(request, 'accounting/journal/journal_entry_create.html', {'ledgers':ledgers, 'sub_ledgers':sub_ledgers}) 

        journal_entry = TblJournalEntry.objects.create(employee_name=request.user.username, journal_total=debit_sum)
        for i in range(len(debit_ledgers)):
            debit_ledger_id = int(debit_ledgers[i])
            debit_ledger = AccountLedger.objects.get(pk=debit_ledger_id)
            debit_particular = debit_particulars[i]
            debit_amount = D(debit_amounts[i])
            subledger = self.get_subledger( debit_subledgers[i], debit_ledger)
            debit_ledger_type = debit_ledger.account_chart.account_type
            TblDrJournalEntry.objects.create(ledger=debit_ledger, journal_entry=journal_entry, particulars=debit_particular, debit_amount=debit_amount, sub_ledger=subledger)
            if debit_ledger_type in ['Asset', 'Expense']:
                debit_ledger.total_value =debit_ledger.total_value + debit_amount
                debit_ledger.save()
                if subledger:
                    subledger.total_value = subledger.total_value + debit_amount
                    subledger.save()

            elif debit_ledger_type in ['Liability', 'Revenue', 'Equity']:
                debit_ledger.total_value = debit_ledger.total_value - debit_amount
                debit_ledger.save()
                if subledger:
                    subledger.total_value = subledger.total_value - debit_amount
                    subledger.save()

        for i in range(len(credit_ledgers)):
            credit_ledger_id = int(credit_ledgers[i])
            credit_ledger = AccountLedger.objects.get(pk=credit_ledger_id)
            credit_particular = credit_particulars[i]
            credit_amount = D(credit_amounts[i])
            subledger = self.get_subledger( credit_subledgers[i], credit_ledger)
            credit_ledger_type = credit_ledger.account_chart.account_type
            TblCrJournalEntry.objects.create(ledger=credit_ledger, journal_entry=journal_entry, particulars=credit_particular, credit_amount=credit_amount, sub_ledger=subledger)
            if credit_ledger_type in ['Asset', 'Expense']:
                credit_ledger.total_value = credit_ledger.total_value - credit_amount
                credit_ledger.save()
                if subledger:
                    subledger.total_value = subledger.total_value - credit_amount
                    subledger.save()
            elif credit_ledger_type in ['Liability', 'Revenue', 'Equity']:
                credit_ledger.total_value = credit_ledger.total_value + credit_amount
                credit_ledger.save()
                if subledger:
                    subledger.total_value = subledger.total_value + credit_amount
                    subledger.save()

        return redirect('journal_list')


class JournalEntryView(IsAdminOrAccountingMixin, View):

    def get(self, request, pk=None):
        from_date = request.GET.get('fromDate', None)
        to_date = request.GET.get('toDate', None)

        if from_date and to_date and (to_date > from_date):
            journals = TblJournalEntry.objects.filter(created_at__range=[from_date, to_date]).order_by('-created_at')

            journal_entries = {
                'entries': [],
                "debit_sum": 0,
                "credit_sum": 0
            }
            debit_sum, credit_sum = 0,0
            for journal in journals:
                data = {'dr':[], 'cr':[], "dr_total": 0, "cr_total": 0}
                for dr in journal.tbldrjournalentry_set.all():
                    data['dr'].append(dr)
                    data['dr_total'] += dr.debit_amount
                for cr in journal.tblcrjournalentry_set.all():
                    data['cr'].append(cr)
                    data['cr_total'] += cr.credit_amount
                journal_entries['entries'].append(data)
                journal_entries['debit_sum']+=data['dr_total']
                journal_entries['credit_sum']+=data['cr_total']


            context = {
                'from_date':from_date,
                'to_date': to_date,
                'journals':journal_entries
            }

            return render(request,'accounting/journal/journal.html' , context=context)
        if pk:
            journal = TblJournalEntry.objects.get(pk=pk)
            credit_details = TblCrJournalEntry.objects.filter(journal_entry=journal)
            debit_details = TblDrJournalEntry.objects.filter(journal_entry=journal)
            debit_total, credit_total = 0, 0
            for dr in debit_details:
                debit_total += dr.debit_amount

            for cr in credit_details:
                credit_total += cr.credit_amount

            context = {
                'credit': credit_details,
                'debit': debit_details,
                "dr_total":debit_total,
                "cr_total": credit_total
            }
            return render(request, 'accounting/journal/journal_voucher.html', context)
            

        journal_entries = TblJournalEntry.objects.prefetch_related('tbldrjournalentry_set').all().order_by('-created_at')
        return render(request, 'accounting/journal/journal_list.html',  {'journal_entries': journal_entries})


class TrialBalanceView(IsAdminOrAccountingMixin, View):

    def filtered_view(self, from_date, to_date):
        filtered_transactions = CumulativeLedger.objects.filter(created_at__range=[from_date, to_date])
        filtered_sum = filtered_transactions.values('ledger_name', 'account_chart__account_type').annotate(Sum('value_changed'))
        trial_balance = []

        total = {'debit_total':0, 'credit_total':0}

        for fil in filtered_sum:
            data = {}
            data['ledger'] = fil['ledger_name']
            account_type = fil['account_chart__account_type']
            if account_type in ['Asset', 'Expense']:
                data['actual_value'] = fil['value_changed__sum']
                if fil['value_changed__sum'] < 0:
                    val = abs(fil['value_changed__sum'])
                    data['credit'] = val
                    data['debit'] = '-'
                    total['credit_total'] += val
                else:
                    val = fil['value_changed__sum']
                    data['debit'] = val
                    data['credit'] = '-'
                    total['debit_total'] += val
            else:
                if fil['value_changed__sum'] < 0:
                    val = abs(fil['value_changed__sum'])
                    data['debit'] = val
                    data['credit'] = '-'
                    total['debit_total'] += val
                else:
                    val = fil['value_changed__sum']
                    data['credit'] = val
                    data['debit'] = '-'
                    total['credit_total'] += val

            if not any(d['account_type'] == account_type for d in trial_balance):
                    trial_balance.append(
                        {
                            'account_type': account_type,
                            'ledgers' : [data]
                        }
                    )
            else:
                for tb in trial_balance:
                    if tb['account_type'] == account_type:
                        tb['ledgers'].append(data)
                        break

        return trial_balance, total

    def detail_view(self, from_date, to_date):
        all_ledgers_list = AccountLedger.objects.values_list('ledger_name', flat=True)
        before_transactions = CumulativeLedger.objects.filter(created_at__lt=from_date, total_value__gt=0).order_by('-created_at')

        trial_balance = []
        total = {'debit_total':0, 'credit_total':0}

        filtered_transactions = CumulativeLedger.objects.filter(created_at__range=[from_date, to_date])
        filtered_sum = filtered_transactions.values('ledger_name', 'account_chart__account_type').annotate(Sum('debit_amount'), Sum('credit_amount'), Sum('value_changed'))

        for fil in filtered_sum:
            data = {}
            data['ledger'] = fil['ledger_name']
            account_type = fil['account_chart__account_type']
            data['debit'] = fil['debit_amount__sum']
            data['credit'] = fil['credit_amount__sum']
            if account_type in ['Asset', 'Expense']:
                if fil['value_changed__sum'] < 0:
                    total['credit_total'] += abs(fil['value_changed__sum'])
                else:
                    total['debit_total'] += abs(fil['value_changed__sum'])
            else:
                if fil['value_changed__sum'] < 0:
                    total['debit_total'] += abs(fil['value_changed__sum'])
                else:
                    total['credit_total'] += abs(fil['value_changed__sum'])



            if not any(d['account_type'] == account_type for d in trial_balance):
                    trial_balance.append(
                        {
                            'account_type': account_type,
                            'ledgers' : [data]
                        }
                    )
            else:
                for tb in trial_balance:
                    if tb['account_type'] == account_type:
                        tb['ledgers'].append(data)
                        break


        included_ledgers = []

        for trans in before_transactions:
            account_type = trans.account_chart.account_type
            if trans.ledger_name not in included_ledgers:
                included_ledgers.append(trans.ledger_name)
                if not any(d['account_type'] == account_type for d in trial_balance):
                    data = {
                        'ledger': trans.ledger_name,
                        'opening': trans.total_value,
                        'debit':'-',
                        'credit':'-',
                        'closing': trans.total_value
                    }
                    trial_balance.append({'account_type':account_type, 'ledgers':[data]})
                else:
                    for tb in trial_balance:
                        if tb['account_type'] == account_type:
                            if not any(d['ledger'] == trans.ledger_name for d in tb['ledgers']):
                                tb['ledgers'].append({
                                    'ledger': trans.ledger_name,
                                    'opening': trans.total_value,
                                    'debit':'-',
                                    'credit':'-',
                                    'closing': trans.total_value
                                })
                            else:
                                for led in tb['ledgers']:
                                    if led['ledger'] == trans.ledger_name:
                                        led['opening'] = trans.total_value
                                        if account_type in ['Asset', 'Expense']:
                                            led['closing'] = trans.total_value + led['debit'] - led['credit']
                                        else:
                                            led['closing'] = trans.total_value + led['credit'] - led['debit']
                                        break


            if len(included_ledgers) >= len(all_ledgers_list):
                break

        # for trans in before_transactions:
        #     if trans.ledger_name not in included_ledgers:
        #         included_ledgers.append(trans.ledger_name)
        #         if not any(d['ledger'] == trans.ledger_name for d in trial_balance):
        #             data = {
        #                 'ledger':trans.ledger_name,
        #                 'opening':trans.total_value,
        #                 'debit':'-',
        #                 'credit':'-',
        #                 'closing':trans.total_value,
        #             }
        #             trial_balance.append(data)
        #         else:
        #             for tb in trial_balance:
        #                 if tb['ledger'] == trans.ledger_name:
        #                     tb['opening'] = trans.total_value
        #                     tb['closing'] = trans.total_value + tb['actual_value']

        #     if len(included_ledgers) >= len(all_ledgers_list):
        #         break
 
        return trial_balance, total



    def get(self, request):
        from_date = request.GET.get('fromDate', None)
        to_date = request.GET.get('toDate', None)
        option = request.GET.get('option', None)

        if from_date and to_date:
            if option and option =='openclose':
                trial_balance, total = self.detail_view(from_date, to_date)
                context = {
                    'trial_balance': trial_balance,
                    "total": total,
                    "from_date":from_date,
                    "to_date":to_date,
                    'openclose':True
                }
                return render(request, 'accounting/trial_balance.html', context)
            else:
                trial_balance, total= self.filtered_view(from_date, to_date)
                context = {
                    'trial_balance': trial_balance,
                    "total": total,
                    "from_date":from_date,
                    "to_date":to_date,
                }

                return render(request, 'accounting/trial_balance.html', context)
        
        else:
            trial_balance = []
            total = {'debit_total':0, 'credit_total':0}
            ledgers = AccountLedger.objects.filter(total_value__gt=0)
            for led in ledgers:
                data = {}
                account_type = led.account_chart.account_type
                data['ledger']=led.ledger_name
                if account_type in ['Asset', 'Expense']:
                    if led.total_value > 0:
                        data['debit'] = led.total_value
                        total['debit_total'] += led.total_value
                        data['credit'] = '-'
                    else:
                        data['credit'] = led.total_value
                        total['credit_total'] += led.total_value
                        data['debit'] = '-'
                else:
                    if led.total_value > 0:
                        data['credit'] = led.total_value
                        total['credit_total'] += led.total_value
                        data['debit'] = '-'
                    else:
                        data['debit'] = led.total_value
                        total['debit_total'] += led.total_value
                        data['credit'] = '-'
                if not any(d['account_type'] == account_type for d in trial_balance):
                    trial_balance.append(
                        {
                            'account_type': account_type,
                            'ledgers' : [data]
                        }
                    )
                else:
                    for tb in trial_balance:
                        if tb['account_type'] == account_type:
                            tb['ledgers'].append(data)
                            break
                            
        # vat_receivable, vat_payable = 0, 0
        # for data in trial_balance:
        #     if data['ledger'] == 'VAT Receivable':
        #         vat_receivable = data['debit']
        #         total['debit_total'] -= data['debit']
        #         trial_balance.remove(data)
        #     if data['ledger'] == 'VAT Payable':
        #         vat_payable = data['credit']
        #         total['credit_total'] -= data['credit']
        #         trial_balance.remove(data)
        # vat_amount = vat_receivable - vat_payable
        # if vat_amount > 0:
        #     trial_balance.append({'ledger':'VAT', 'account_head':'Asset', 'debit':vat_amount, 'credit':'-'})
        #     total['debit_total'] += vat_amount
        # elif vat_amount < 0:
        #     trial_balance.append({'ledger':'VAT', 'account_head':'Liability', 'debit':'-', 'credit':abs(vat_amount)})
        #     total['credit_total'] += abs(vat_amount)

        context = {
            'trial_balance': trial_balance,
            "total": total,
            "from_date":from_date,
            "to_date":to_date
        }
        return render(request, 'accounting/trial_balance.html', context)


class ProfitAndLoss(IsAdminOrAccountingMixin, TemplateView):
    template_name = "accounting/profit_and_loss.html"

    def get_context_data(self, **kwargs):
        org = Organization.objects.first()
        from_date = self.request.GET.get('fromDate', None)
        to_date = self.request.GET.get('toDate', None)
        context = super().get_context_data(**kwargs)
        if from_date and to_date:
            expenses = AccountLedger.objects.filter(account_chart__account_type="Expense", total_value__gt=0, created_at__range=[from_date, to_date])
            revenues = AccountLedger.objects.filter(account_chart__account_type="Revenue", total_value__gt=0, created_at__range=[from_date, to_date])
        else:
            expenses = AccountLedger.objects.filter(account_chart__account_type="Expense", total_value__gt=0)
            revenues = AccountLedger.objects.filter(account_chart__account_type="Revenue", total_value__gt=0)

        revenue_list= []
        revenue_total = 0
        expense_list= []
        expense_total = 0

        for revenue in revenues:
            revenue_list.append({'title':revenue.ledger_name, 'amount': revenue.total_value})
            revenue_total += revenue.total_value

        for expense in expenses:
            expense_list.append({'title':expense.ledger_name, 'amount': expense.total_value})
            expense_total += expense.total_value

        context['expenses'] = expense_list
        context['expense_total'] = expense_total
        context['revenues'] = revenue_list
        context['revenue_total'] = revenue_total
        context['org'] = org
        return context
    

class BalanceSheet(IsAdminOrAccountingMixin, TemplateView):
    template_name = "accounting/balance_sheet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org= Organization.objects.first()

        asset_dict = {}
        liability_dict = {}

        assets = AccountChart.objects.filter(account_type='Asset')
        for ledger in assets:
            sub = AccountLedger.objects.filter(account_chart__group=ledger, total_value__gt=0)
            if sub:
                asset_dict[ledger.group] = sub


        liabilities = AccountChart.objects.filter(Q(account_type="Liability") | Q(account_type="Equity") )
        for ledger in liabilities:
            sub = AccountLedger.objects.filter(account_chart__group=ledger, total_value__gt=0)
            if sub:
                liability_dict[ledger.group] = sub

        asset_total = AccountLedger.objects.filter(account_chart__account_type='Asset').aggregate(Sum('total_value')).get('total_value__sum')
        liability_total = AccountLedger.objects.filter(Q(account_chart__account_type="Liability") | Q(account_chart__account_type="Equity") )\
                                    .aggregate(Sum('total_value')).get('total_value__sum')
        

        if asset_total and liability_total:
            if asset_total > liability_total:
                context['lib_retained_earnings'] =  asset_total-liability_total
                context['liability_total'] = liability_total + asset_total-liability_total
                context['asset_total'] = asset_total

            else:
                context['asset_retained_earnings'] =  liability_total-asset_total
                context['asset_total'] = asset_total + liability_total-asset_total
                context['liability_total'] = liability_total
            

        context['assets'] = asset_dict
        context['liabilities'] =  liability_dict
        context['org'] =  org


        return context


class DepreciationView(IsAdminOrAccountingMixin, View):

    def get(self, request):
        depreciations = Depreciation.objects.all()
        return render(request, 'accounting/depreciation_list.html', {'depreciations':depreciations})


@api_view(['POST'])
def end_fiscal_year(request):
        org = Organization.objects.first()
        fiscal_year = org.get_fiscal_year()
        ledgers = AccountLedger.objects.all()
        sub_ledgers = AccountSubLedger.objects.all()
        accumulated_depn = AccountLedger.objects.get(ledger_name='Accumulated Depreciation')


        for sub in sub_ledgers:
            FiscalYearSubLedger.objects.create(sub_ledger_name=sub.sub_ledger_name, total_value=sub.total_value, fiscal_year=fiscal_year, ledger=sub.ledger)

        for led in ledgers:
            FiscalYearLedger.objects.create(ledger_name=led.ledger_name, total_value=led.total_value,fiscal_year=fiscal_year, account_chart=led.account_chart)
            if led.account_chart.account_type in ['Revenue', 'Expense']:
                for sub in led.accountsubledger_set.all():
                    if sub.ledger.account_chart.group == 'Depreciation':
                        accumulated_depn.total_value += sub.total_value
                        accumulated_depn.save()
                    sub.total_value=0
                    sub.save()
                if not led.ledger_name == 'Accumulated Depreciation':
                    led.total_value = 0
                    led.save()
                    # AccountSubLedger.objects.create(sub_ledger_name=f'{sub.sub_ledger_name} for {fiscal_year}', total_value=sub.total_value, ledger=accumulated_depn)
                    
        depreciations = Depreciation.objects.filter(fiscal_year=fiscal_year)

        org.start_year+=1
        org.end_year += 1

        org.save()

        for depn in depreciations:
            amount = float(depn.net_amount)
            percentage = depn.item.asset.depreciation_pool.percentage
            bill_date = depn.item.asset_purchase.bill_date
            depreciation_amount, bs_date = calculate_depreciation(amount, percentage, bill_date)
            net_amount = amount-depreciation_amount
            Depreciation.objects.create(miti=bs_date,depreciation_amount=depreciation_amount, net_amount=net_amount, item=depn.item, ledger=depn.ledger)
            depreciation_amount = D(depreciation_amount)
            depn_subledger = AccountSubLedger.objects.get(sub_ledger_name=f'{depn.item.asset.title} Depreciation')
            depn_subledger.total_value += depreciation_amount
            depn_subledger.save()


            depn_ledger = depn_subledger.ledger
            depn_ledger.total_value+= depreciation_amount
            depn_ledger.save()

            asset_ledger = depn.ledger
            asset_ledger.total_value -= depreciation_amount
            asset_ledger.save()

            asset_ledger = AccountSubLedger.objects.get(sub_ledger_name=depn.item.asset.title, ledger__account_chart__account_type='Asset')
            asset_ledger.total_value -= depreciation_amount
            asset_ledger.save()
        
        
        return Response({})

        











