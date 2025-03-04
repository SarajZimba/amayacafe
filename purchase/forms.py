from django import forms
from .models import Vendor, ProductPurchase
from root.forms import BaseForm
from product.models import Product
from accounting.models import AccountChart, AccountLedger

class VendorForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'address', 'contact', 'pan_no']


class ProductPurchaseForm(BaseForm, forms.ModelForm):
    DISCOUNT_PERCENTAGE_CHOICES = (
        (0,0),
        (5,5),
        (10, 10),
        (20, 20),
        (30, 30),
        (40, 40),
        (50, 50),

    )
    bill_date = forms.DateField(required=True)
    bill_no = forms.CharField(required=False, empty_value=None)
    pp_no = forms.CharField(required=False, empty_value=None)

    vendor = forms.ModelChoiceField(
        queryset=Vendor.objects.active(),
    )
    sub_total = forms.FloatField()
    discount_percentage = forms.ChoiceField(choices=DISCOUNT_PERCENTAGE_CHOICES)
    discount_amount = forms.FloatField(initial=0.0)

    taxable_amount = forms.FloatField(initial=0.0)
    non_taxable_amount = forms.FloatField(initial=0.0)

    tax_amount = forms.FloatField(initial=0.0)
    grand_total = forms.FloatField()
    amount_in_words = forms.CharField()
    payment_mode = forms.ChoiceField(
        choices=[
            ("", "-----------------"),
            ("Cash", "Cash"),
            ("Credit", "Credit"),
            ("Credit Card", "Credit Card"),
            ("Mobile Payment", "Mobile Payment"),
            ("Complimentary", "Complimentary"),
        ],
        required=True,
    )


    field_order = [ 'bill_no', 'bill_date', 'pp_no', 'vendor', 'product', 'sub_total', 'discount_percentage', 'discount_amount', 'taxable_amount',
                'non_taxable_amount', 'tax_amount', 'grand_total', 'amount_in_words', 'payment_mode', 'debit_account']

    class Meta:
        model = ProductPurchase
        exclude = 'created_at', 'updated_at', 'sorting_order', 'is_featured', 'status', 'is_deleted', 'purchase', 'rate', 'quantity', 'item_total'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sub_total"].widget.attrs["readonly"] = True
        self.fields["taxable_amount"].widget.attrs["readonly"] = True
        self.fields["non_taxable_amount"].widget.attrs["readonly"] = True
        self.fields["tax_amount"].widget.attrs["readonly"] = True
        self.fields["grand_total"].widget.attrs["readonly"] = True
        self.fields["tax_amount"].label = "VAT Amount"
        self.fields["discount_amount"].widget.attrs["readonly"] = True
        self.fields["amount_in_words"].widget.attrs["readonly"] = True
        self.fields["debit_account"] = forms.ModelChoiceField( queryset=AccountLedger.objects.filter(account_chart=AccountChart.objects.filter(group="Purchases").first()))
        self.fields["debit_account"].widget.attrs = {
            "tags":"true",
            "class":"form-select",
            "data-control": "select2",
            "data-placeholder": "Select Account",
        }

        self.fields['product'].widget.queryset = Product.objects.filter(is_produced=False)
        self.fields['bill_date'].widget.attrs["required"] = True



    def clean_product(self):
        return self.cleaned_data.get('product')
    
    def clean(self):
        cleaned_data = super().clean()
        if 'product' in cleaned_data:
            cleaned_data['product'] = self.cleaned_data['product']
        
        return cleaned_data

"""  Asset Purchase  """

from .models import AssetPurchase, Asset

class AssetPurchaseForm(BaseForm, forms.ModelForm):
    assets = forms.ModelChoiceField(
        queryset=Asset.objects.all()
    )
    vendor = forms.ModelChoiceField(
        queryset=Vendor.objects.all()
    )
    # debit_account =  forms.ModelChoiceField( queryset=AccountLedger.objects.filter(account_chart=AccountChart.objects.filter(ledger="Fixed Assets").first()))
    

    field_order = [ 'bill_no', 'bill_date', 'pp_no', 'vendor', 'assets', 'sub_total', 'discount_percentage', 'discount_amount', 'taxable_amount',
                'non_taxable_amount', 'tax_amount', 'grand_total', 'amount_in_words', 'payment_mode', "debit_acocunt"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sub_total"].widget.attrs["readonly"] = True
        self.fields["taxable_amount"].widget.attrs["readonly"] = True
        self.fields["non_taxable_amount"].widget.attrs["readonly"] = True
        self.fields["tax_amount"].widget.attrs["readonly"] = True
        self.fields["grand_total"].widget.attrs["readonly"] = True
        self.fields["tax_amount"].label = "VAT Amount"
        self.fields["discount_amount"].widget.attrs["readonly"] = True
        self.fields["amount_in_words"].widget.attrs["readonly"] = True
        self.fields["debit_account"] = forms.ModelChoiceField( queryset=AccountLedger.objects.filter(account_chart=AccountChart.objects.filter(group="Fixed Assets").first()))
        self.fields["debit_account"].widget.attrs = {
            "tags":"true",
            "class":"form-select",
            "data-control": "select2",
            "data-placeholder": "Select Account",
        }

    class Meta:
        model = AssetPurchase
        fields = '__all__'
        exclude = ['is_deleted', 'status', 'deleted_at', 'sorting_order', 'is_featured']


from .models import Production
class ProductionForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Production
        fields = '__all__'
        exclude = ['is_deleted', 'status', 'deleted_at', 'sorting_order', 'is_featured']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'] = forms.ModelChoiceField(queryset=Product.objects.filter(is_produced=True))
        self.fields["product"].widget.attrs = {
            "class":"form-select",
            "data-control": "select2",
            "data-placeholder": "Select Item",
        }
