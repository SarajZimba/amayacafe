from datetime import date, datetime
from django.forms.models import BaseModelForm
from django.urls import reverse_lazy
from django.db.models import Sum
from django.db.utils import IntegrityError

from django.views.generic import CreateView,DetailView,ListView,UpdateView,View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from accounting.models import TblCrJournalEntry, TblDrJournalEntry, TblJournalEntry, AccountLedger, AccountChart, AccountSubLedger, Depreciation
from accounting.utils import calculate_depreciation
from root.utils import DeleteMixin
from product.models import Product, ProductCategory
from organization.models import Organization
from product.models import ProductStock
from .forms import VendorForm, ProductPurchaseForm
from .models import Vendor, ProductPurchase, Purchase, TblpurchaseEntry, TblpurchaseReturn
import decimal
from bill.views import ExportExcelMixin
import json

class VendorMixin:
    model = Vendor
    form_class = VendorForm
    paginate_by = 10
    queryset = Vendor.objects.filter(status=True,is_deleted=False)
    success_url = reverse_lazy('vendor_list')



class VendorList(VendorMixin, ListView):
    template_name = "vendor/vendor_list.html"
    queryset = Vendor.objects.filter(status=True,is_deleted=False)


class VendorDetail(VendorMixin, DetailView):
    template_name = "vendor/vendor_detail.html"


class VendorCreate(VendorMixin, CreateView):
    template_name = "create.html"


class VendorUpdate(VendorMixin, UpdateView):
    template_name = "update.html"


class VendorDelete(VendorMixin, DeleteMixin, View):
    pass

'''  -------------------------------------    '''


class ProductPurchaseCreateView(CreateView):
    model = ProductPurchase
    form_class = ProductPurchaseForm
    template_name = "purchase/purchase_create.html"

    def create_subledgers(self, product, item_total, debit_account):
        debit_account = get_object_or_404(AccountLedger, pk=int(debit_account))
        subledgername = f'{product.title} ({product.type.title})'
        try:
            sub = AccountSubLedger.objects.get(sub_ledger_name=subledgername, ledger=debit_account)
            sub.total_value += decimal.Decimal(item_total)
            sub.save()
        except AccountSubLedger.DoesNotExist:
            AccountSubLedger.objects.create(sub_ledger_name=subledgername, ledger=debit_account, total_value=item_total)

    def create_accounting(self, debit_account_id, payment_mode:str, username:str, sub_total, tax_amount, vendor):
        sub_total = decimal.Decimal(sub_total)
        tax_amount = decimal.Decimal(tax_amount)
        total_amount =  sub_total+ tax_amount

        cash_ledger = get_object_or_404(AccountLedger, ledger_name='Cash-In-Hand')
        vat_receivable = get_object_or_404(AccountLedger, ledger_name='VAT Receivable')
        debit_account = get_object_or_404(AccountLedger, pk=int(debit_account_id))
        
        journal_entry = TblJournalEntry.objects.create(employee_name=username, journal_total = total_amount)
        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Automatic: {debit_account.ledger_name} A/c Dr.", debit_amount=sub_total, ledger=debit_account)
        debit_account.total_value += sub_total
        debit_account.save()
        if tax_amount > 0:
            TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars="Automatic: VAT Receivable A/c Dr.", debit_amount=tax_amount, ledger=vat_receivable)
            vat_receivable.total_value += tax_amount
            vat_receivable.save()
        if payment_mode == "Credit":
            try:
                vendor_ledger = AccountLedger.objects.get(ledger_name=vendor)
                vendor_ledger.total_value += total_amount
                vendor_ledger.save()
            except AccountLedger.DoesNotExist:
                chart = AccountChart.objects.get(group='Sundry Creditors')
                vendor_ledger = AccountLedger.objects.create(ledger_name=vendor, total_value=total_amount, is_editable=True, account_chart=chart)
            TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Automatic: To {vendor_ledger.ledger_name} A/c", credit_amount=total_amount, ledger=vendor_ledger)
        else:
            TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Automatic: To {cash_ledger.ledger_name} A/c", credit_amount=total_amount, ledger=cash_ledger)
            cash_ledger.total_value -= total_amount
            cash_ledger.save()


    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        return self.form_valid(form)

    def form_valid(self, form):
        form_data = form.data
        bill_no = form_data.get('bill_no', None)
        bill_date = form_data.get('bill_date', None)
        pp_no = form_data.get('pp_no',None)
        vendor_id = form_data.get('vendor')
        sub_total = form_data.get('sub_total')
        discount_percentage = form_data.get('discount_percentage')
        discount_amount = form_data.get('discount_amount')
        taxable_amount = form_data.get('taxable_amount')
        non_taxable_amount = form_data.get('non_taxable_amount')
        tax_amount = form_data.get('tax_amount')
        grand_total = form_data.get('grand_total')
        amount_in_words = form_data.get('amount_in_words')
        payment_mode = form_data.get('payment_mode')
        debit_account = form_data.get('debit_account')
        purchase_object = Purchase(
            bill_no=bill_no,
            vendor_id=vendor_id,sub_total=sub_total, bill_date=bill_date,
            discount_percentage=discount_percentage,discount_amount=discount_amount,
            taxable_amount=taxable_amount, non_taxable_amount=non_taxable_amount,
            tax_amount=tax_amount, grand_total=grand_total,
            amount_in_words=amount_in_words, payment_mode=payment_mode
        )
        purchase_object.save()

        product_ids =  form_data.get('product_id_list', '')
        product_taxable_info = form_data.get('product_taxable_info', '')
        new_items_name = {}
        if product_taxable_info and len(product_taxable_info) > 0:
            new_items_name = json.loads(product_taxable_info)

        item_name = ''

        total_quantity = 0
        vendor = Vendor.objects.get(pk=vendor_id)
        vendor_name = vendor.name
        vendor_pan = vendor.pan_no

        if product_ids:
            product_ids = product_ids.split(',')

        for id in product_ids:
            try:
                id = int(id)
                quantity = int(form_data.get(f'id_bill_item_quantity_{id}'))
                total_quantity += quantity
                prod = Product.objects.get(pk=id)
                item_name += prod.title +'-'+ str(quantity) + ', '
                rate = float(form_data.get(f'id_bill_item_rate_{id}'))
                item_total = quantity * rate
                self.create_subledgers(prod, item_total, debit_account)
                ProductPurchase.objects.create(product_id=id, purchase=purchase_object, quantity=quantity, rate=rate, item_total=item_total)
            except ValueError:
                pass

        if new_items_name:
            for k, v in new_items_name.items():
                other_cat = ProductCategory.objects.get(title__iexact="others").pk
                product_title = k
                rate = float(form_data.get(f'id_bill_item_rate_{k}'))
                quantity = int(form_data.get(f'id_bill_item_quantity_{k}'))
                item_total = quantity * rate
                is_taxable = True if v == "true" or v == True else False
                try:
                    prod = Product.objects.create(title=product_title, is_taxable=is_taxable, group='others', type_id=other_cat, cost_price=rate)
                except IntegrityError:
                    prod = Product.objects.get(title=k)
                    
                self.create_subledgers(prod, item_total, debit_account)
                ProductPurchase.objects.create(product=prod, purchase=purchase_object, quantity=quantity, rate=rate, item_total=item_total)

        TblpurchaseEntry.objects.create(
            bill_no=bill_no, bill_date=bill_date, pp_no=pp_no, vendor_name=vendor_name, vendor_pan=vendor_pan,
            item_name=item_name, quantity=total_quantity, amount=grand_total, tax_amount=tax_amount, non_tax_purchase=non_taxable_amount
        )
        vendor_detail = str(vendor.pk)+' '+ vendor_name
        self.create_accounting(debit_account_id=debit_account, payment_mode=payment_mode, username=self.request.user.username, sub_total=sub_total, tax_amount=tax_amount, vendor=vendor_detail)

        return redirect('/purchase/' )
    


class PurchaseListView(ListView):
    model = Purchase
    queryset = Purchase.objects.filter(is_deleted=False)
    template_name = 'purchase/purchase_list.html'


class PurchaseDetailView(DetailView):
    template_name = 'purchase/purchase_detail.html'
    queryset = Purchase.objects.filter(is_deleted=False)

    def get_context_data(self, **kwargs):
        org = Organization.objects.first()
        context =  super().get_context_data(**kwargs)
        context['organization'] = org
        return context



class MarkPurchaseVoid(View):

    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        reason = request.POST.get('voidReason')
        purchase = get_object_or_404(Purchase, pk=id)
        purchase.status = False
        purchase.save()


        purchased_products = purchase.productpurchase_set.all()
        for item in purchased_products:
            stock = ProductStock.objects.get(product=item.product)
            stock.stock_quantity = stock.stock_quantity-item.quantity
            stock.save()
            

        entry_obj = TblpurchaseEntry.objects.get(pk=id)
        TblpurchaseReturn.objects.create(
            bill_date=entry_obj.bill_date,
            bill_no=entry_obj.bill_no,
            pp_no=entry_obj.pp_no,
            vendor_name=entry_obj.vendor_name,
            vendor_pan=entry_obj.vendor_pan,
            item_name=entry_obj.item_name,
            quantity=entry_obj.quantity,
            unit=entry_obj.unit,
            amount=entry_obj.amount,
            tax_amount=entry_obj.tax_amount,
            non_tax_purchase=entry_obj.non_tax_purchase,
            reason = reason
        )
        
        
        return redirect(
            reverse_lazy("purchase_detail", kwargs={"pk": id})
        )


""" View starting for Purchase Book  """

class PurchaseBookListView(ExportExcelMixin,View):

    def export_to_excel(self, data):
        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = 'attachment; filename="purchase_book.xls"'

        common = ['bill_date', "bill_no", "pp_no", "vendor_name", "vendor_pan", "amount", "tax_amount", "non_tax_purchase"]
        common.insert(0, 'idtblpurchaseEntry')
        extra = ["import","importCountry","importNumber", "importDate"]
        

        wb, ws, row_num, font_style_normal, font_style_bold = self.init_xls(
            "Purchase Book", common+extra
        )
        purchase_entry = data.get('purchase_entry')
        rows = purchase_entry.values_list(*common)

        for row in rows:
            row = row + (0,0,0,0)
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style_normal)

        purchase_entry_sum = data.get('purchase_entry_sum')

        row_num += 1
        ws.write(row_num, 0, "Total", font_style_normal)
        for key, value in purchase_entry_sum.items():
            key = key.split('__')[0]
            ws.write(row_num, common.index(key), value or 0, font_style_normal)

        common [0] = "idtblpurchaseReturn"
        columns2 = common+extra

        row_num += 1
        ws.write(row_num, 0, "")
        row_num += 1
        ws.write(row_num, 0, "Purchase Return", font_style_bold)
        row_num += 1

        new_columns = ["id"] + columns2[1:]
        for col_num in range(len(columns2)):
            ws.write(row_num, col_num, new_columns[col_num], font_style_bold)

        return_entry = data.get('return_entry')
        rows2 = return_entry.values_list(*common)
        return_entry_sum = data.get('return_entry_sum')

        for row in rows2:
            row = row + (0,0,0,0)
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style_normal)

        row_num += 1
        ws.write(row_num, 0, "Total", font_style_normal)
        for key, value in return_entry_sum.items():
            key = key.split('__')[0]
            ws.write(row_num, common.index(key), value or 0, font_style_normal)


        row_num += 2
        ws.write(row_num, 0, "Grand Total", font_style_bold)

        grand_total = data.get('grand_total')

        for key, value in grand_total.items():
            key = key.split('__')[0]
            ws.write(row_num, common.index(key), value or 0, font_style_bold)
        wb.save(response)
        return response


    def get(self, request, *args, **kwargs):
        today = date.today()
        from_date = request.GET.get('fromDate', today)
        to_date = request.GET.get('toDate', today)
        format = request.GET.get('format', None)

        purchase_entry = TblpurchaseEntry.objects.filter(bill_date__range=[from_date, to_date])
        return_entry = TblpurchaseReturn.objects.filter(bill_date__range=[from_date, to_date])
        purchase_entry_sum = dict()
        return_entry_sum = dict()
        grand_total = dict()

        if purchase_entry and return_entry:
            purchase_entry_sum = purchase_entry.aggregate(Sum('amount'), Sum('tax_amount'), Sum('non_tax_purchase'))
            return_entry_sum = return_entry.aggregate(Sum('amount'), Sum('tax_amount'), Sum('non_tax_purchase'))

            for key in purchase_entry_sum.keys():
                grand_total[key] = purchase_entry_sum[key] - return_entry_sum[key]


        context = {'purchase_entry':purchase_entry, 'return_entry':return_entry,
                    'purchase_entry_sum':purchase_entry_sum, 'return_entry_sum': return_entry_sum, 'grand_total': grand_total}
        
        if format and format =='xls':
            return self.export_to_excel(data=context)


        return render(request, 'purchase/purchase_book.html', context)


class VendorWisePurchaseView(ExportExcelMixin, View):

    def export_to_excel(self, data):
        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = 'attachment; filename="vendor_wise_purchase.xls"'
        columns = ['vendor', 'bill_date', "bill_no", "item", "group", "rate", "quantity", "unit", "tax_amount", "total_amount"]
        wb, ws, row_num, font_style_normal, font_style_bold = self.init_xls(
            "Vendor wise Purchase", columns=columns
        )

        new_data = []
        for d in data:
            new_data.append([d['name']])

            for purchase in d['purchases']:
                for item in purchase.productpurchase_set.all():
                    items_array = ['',purchase.bill_date.strftime('%Y-%m-%d'), purchase.bill_no]
                    items_array.append(item.product.title)
                    items_array.append(item.product.group)
                    items_array.append(item.rate)
                    items_array.append(item.quantity)
                    items_array.append(item.product.unit)
                    items_array.append(purchase.tax_amount)
                    items_array.append(purchase.grand_total)
                    new_data.append(items_array)
        for row in new_data:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style_normal)
        wb.save(response)
        return response
        
        

    def get(self, request):
        from_date = request.GET.get('fromDate')
        to_date = request.GET.get('toDate')
        format = request.GET.get('format')

        vendors = { v[0]:{'id':v[1], 'name':v[0], 'purchases':[]} for v in Vendor.objects.values_list('name', 'id')}
        if from_date and to_date:
            purchases = Purchase.objects.filter(bill_date__range=[from_date, to_date])
        else:
            purchases = Purchase.objects.all()
        for purchase in purchases:
            if purchase.vendor:
                vendor = vendors.get(purchase.vendor.name)
                vendor['purchases'].append(purchase)
            
        data = [i for i in vendors.values()]
        if format and format.lower().strip() == 'xls':
            return self.export_to_excel(data)
        

        return render(request, 'purchase/vendorwisepurchase.html', {'object_list':data})




"""  ***************   Asset Purchase  ****************  """


from .models import AssetPurchase, Asset, AssetPurchaseItem
from .forms import AssetPurchaseForm

class AssetPurchaseMixin:
    model = AssetPurchase
    form_class = AssetPurchaseForm
    paginate_by = 10
    queryset = AssetPurchase.objects.filter(status=True,is_deleted=False)
    success_url = reverse_lazy('assetpurchase_list')

class AssetPurchaseList(AssetPurchaseMixin, ListView):
    template_name = "assetpurchase/assetpurchase_list.html"
    queryset = AssetPurchase.objects.filter(status=True,is_deleted=False)

class AssetPurchaseDetail(AssetPurchaseMixin, DetailView):
    template_name = "assetpurchase/assetpurchase_detail.html"


class AssetPurchaseUpdate(AssetPurchaseMixin, UpdateView):
    template_name = "update.html"

# class AssetPurchaseDelete(AssetPurchaseMixin, DeleteMixin, View):
#     pass

class AssetPurchaseCreate(CreateView):
    model = AssetPurchase
    form_class = AssetPurchaseForm
    template_name = "assetpurchase/assetpurchase_create.html"

    def post(self, request):
        bill_no = request.POST.get('bill_no', None)
        bill_date = request.POST.get('bill_date', None)
        vendor_id = request.POST.get('vendor')
        sub_total = request.POST.get('sub_total')
        discount_percentage = request.POST.get('discount_percentage')
        discount_amount = request.POST.get('discount_amount')
        taxable_amount = request.POST.get('taxable_amount')
        non_taxable_amount = request.POST.get('non_taxable_amount')
        tax_amount = request.POST.get('tax_amount')
        grand_total = request.POST.get('grand_total')
        amount_in_words = request.POST.get('amount_in_words')
        payment_mode = request.POST.get('payment_mode')
        debit_account = request.POST.get('debit_account', None)


        vendor=None
        try:
            v_id = int(vendor_id)
            vendor = Vendor.objects.get(pk=v_id)
        except Exception as e:
            vendor = Vendor.objects.create(name=vendor_id)
        
        asset_purchase = AssetPurchase(
            bill_no=bill_no,
            vendor=vendor,sub_total=sub_total, bill_date=bill_date,
            discount_percentage=discount_percentage,discount_amount=discount_amount,
            taxable_amount=taxable_amount, non_taxable_amount=non_taxable_amount,
            tax_amount=tax_amount, grand_total=grand_total,
            amount_in_words=amount_in_words, payment_mode=payment_mode
        )
        asset_purchase.save()


        selected_item_list = request.POST.get('select_items_list', [])
        selected_item_list = selected_item_list.split(',')

        debit_ledger = AccountLedger.objects.get(pk=int(debit_account))
        depn_group, _ = AccountChart.objects.get_or_create(group='Depreciation')
        depn_ledger, _ = AccountLedger.objects.get_or_create(account_chart=depn_group, ledger_name=f"{debit_ledger.ledger_name} Depreciation")
        total_depreciation_amount = 0
        for item in selected_item_list:
            if not Asset.objects.filter(title=item).exists():
                depn = int(request.POST.get(f'id_depn_{item}'))
                asset = Asset.objects.create(title=item, depreciation_pool_id=int(depn))
            else:
                asset = Asset.objects.get(title=item)
            quantity = int(request.POST.get(f'id_bill_item_quantity_{item}'))
            rate = float(request.POST.get(f'id_bill_item_rate_{item}'))
            item_total = rate * quantity
            item_purchased = AssetPurchaseItem.objects.create(asset=asset, asset_purchase=asset_purchase, rate=rate, quantity=quantity, item_total=item_total)

            depreciation_amount, miti = calculate_depreciation(item_total, asset.depreciation_pool.percentage, bill_date)
            depreciation_amount = decimal.Decimal(depreciation_amount)
            net_amount = decimal.Decimal(item_total)-depreciation_amount

            try:
                subled = AccountSubLedger.objects.get(sub_ledger_name=f'{asset.title}', ledger=debit_ledger)
                subled.total_value += net_amount
                subled.save()
            except AccountSubLedger.DoesNotExist:
                AccountSubLedger.objects.create(sub_ledger_name=f'{asset.title}', total_value= net_amount, ledger=debit_ledger)

            Depreciation.objects.create(item=item_purchased, miti=miti, depreciation_amount=depreciation_amount, net_amount=net_amount, ledger=debit_ledger)

            try:
                sub_led = AccountSubLedger.objects.get(sub_ledger_name=f"{asset.title} Depreciation",ledger=depn_ledger)
                sub_led.total_value += depreciation_amount
                sub_led.save()
            except AccountSubLedger.DoesNotExist:
                AccountSubLedger.objects.create(sub_ledger_name=f"{asset.title} Depreciation",ledger=depn_ledger,total_value=depreciation_amount)

            depn_ledger.total_value += depreciation_amount
            total_depreciation_amount+= depreciation_amount
            depn_ledger.save()

        if payment_mode != 'Credit':
            if debit_account:
                try:
                    credit_ledger = AccountLedger.objects.get(ledger_name='Cash-In-Hand')
                    journal_entry = TblJournalEntry.objects.create(employee_name=request.user.username)

                    grand_total = decimal.Decimal(grand_total)
                    tax_amt = decimal.Decimal(tax_amount)

                    total_debit_amt = grand_total - tax_amt
                    
                    if tax_amt > 0:
                        vat_receivable =  AccountLedger.objects.get(ledger_name='VAT Receivable')
                        vat_receivable.total_value += tax_amt
                        vat_receivable.save()
                        TblDrJournalEntry.objects.create(ledger=vat_receivable, journal_entry=journal_entry, particulars=f'Vat receivable from {bill_no}', debit_amount=tax_amt)

                    TblDrJournalEntry.objects.create(ledger=debit_ledger, journal_entry=journal_entry, particulars=f'Debit from bill {bill_no}', debit_amount=total_debit_amt)
                    debit_ledger.total_value += total_debit_amt
                    debit_ledger.save()
                    TblCrJournalEntry.objects.create(ledger=credit_ledger, journal_entry=journal_entry,particulars=f'Cash cr. from bill {bill_no}', credit_amount=grand_total)
                    credit_ledger.total_value -= grand_total
                    credit_ledger.save()
                    journal_entry.journal_total = total_debit_amt
                    journal_entry.save()
                except Exception as e:
                    print(e)
        else:
            if debit_account:
                vendor_name = vendor.name
                try:
                    credit_ledger = None
                    if not AccountLedger.objects.filter(ledger_name=vendor_name).exists():
                        account_chart = AccountChart.objects.get(group='Sundry Creditors')
                        credit_ledger = AccountLedger(ledger_name=vendor_name, account_chart=account_chart)
                        credit_ledger.save()
                        
                    credit_ledger = AccountLedger.objects.get(ledger_name=vendor_name)
                    debit_ledger = AccountLedger.objects.get(pk=int(debit_account))
                    journal_entry = TblJournalEntry.objects.create(employee_name=request.user.username)

                    grand_total = decimal.Decimal(grand_total)
                    tax_amt = decimal.Decimal(tax_amount)

                    total_debit_amt = grand_total - tax_amt
                    
                    if tax_amt > 0:
                        vat_receivable =  AccountLedger.objects.get(ledger_name='VAT Receivable')
                        vat_receivable.total_value += tax_amt
                        vat_receivable.save()
                        TblDrJournalEntry.objects.create(ledger=vat_receivable, journal_entry=journal_entry, particulars=f'Vat receivable from {bill_no}', debit_amount=tax_amt)

                    TblDrJournalEntry.objects.create(ledger=debit_ledger, journal_entry=journal_entry, particulars=f'Debit from bill {bill_no}', debit_amount=total_debit_amt)
                    debit_ledger.total_value += total_debit_amt
                    debit_ledger.save()
                    TblCrJournalEntry.objects.create(ledger=credit_ledger, journal_entry=journal_entry,particulars=f'Cash cr. from bill {bill_no}', credit_amount=grand_total)
                    credit_ledger.total_value += grand_total
                    credit_ledger.save()

                    journal_entry.journal_total = grand_total
                    journal_entry.save()
                except Exception as e:
                    print(e)

        debit_ledger.total_value -= total_depreciation_amount
        debit_ledger.save()

        return redirect('/asset/')
    

from .models import Production
from .forms import ProductionForm
class ProductionMixin:
    model = Production
    form_class = ProductionForm
    paginate_by = 10
    queryset = Production.objects.filter(status=True,is_deleted=False)
    success_url = reverse_lazy('production_list')

class ProductionList(ProductionMixin, ListView):
    template_name = "production/production_list.html"
    queryset = Production.objects.filter(status=True,is_deleted=False)

class ProductionDetail(ProductionMixin, DetailView):
    template_name = "production/production_detail.html"

class ProductionCreate(ProductionMixin, CreateView):
    template_name = "production/production_create.html"

    def post(self, request):
        return redirect(self.success_url)

class ProductionUpdate(ProductionMixin, UpdateView):
    template_name = "update.html"

class ProductionDelete(ProductionMixin, DeleteMixin, View):
    pass
