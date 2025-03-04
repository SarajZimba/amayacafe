from django import forms
from django.forms.models import inlineformset_factory, formset_factory
from django.utils.functional import lazy
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from root.forms import BaseForm  # optional

from .models import Bill, BillItem, tbldeliveryhistory
from product.models import Product


class BillForm(BaseForm, forms.ModelForm):
    amount_in_words = forms.CharField(
        widget=forms.Textarea(attrs={"rows": "1"}),
        required=True,
    )
    product = forms.ModelMultipleChoiceField(
        queryset=Product.objects.active().order_by('title'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    # is_taxable = forms.BooleanField(required=False, initial=False)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sub_total"].widget.attrs["readonly"] = True
        self.fields["taxable_amount"].widget.attrs["readonly"] = True
        self.fields["tax_amount"].widget.attrs["readonly"] = True
        self.fields["amount_in_words"].widget.attrs["readonly"] = True
        self.fields["grand_total"].widget.attrs["readonly"] = True
        self.fields["tax_amount"].label = "VAT Amount"
        self.fields["discount_amount"].widget.attrs["min"] = 0
        self.fields["customer"].label = lazy(
            lambda: format_html(
                "Customer <a href='%s' a>Create</a>" % reverse("user:customer_create")
            )
        )
        self.fields['customer'].required = False


    class Meta:

        model = Bill
        fields = [
            "customer",
            "customer_name",
            "customer_tax_number",
            "customer_address",
            # "transaction_miti",
            "product",
            # "bill_items",
            "sub_total",
            "discount_amount",
            # "is_taxable",
            "taxable_amount",
            "tax_amount",
            "grand_total",
            "amount_in_words",
            "payment_mode",
        ]
        labels = {"customer_tax_number": "Customer PAN Number"}
        widgets = {
            "customer": forms.Select(
                attrs={
                    "class": "form-select",
                    "data-control": "select2",
                    "data-placeholder": "Select Customer",
                    'required':False
                }
            ),
        }


class DeliveryForm(BaseForm, forms.ModelForm):
    class Meta:
        model = tbldeliveryhistory
        fields = "__all__"
        exclude = [
            "is_deleted",
            "status",
            "deleted_at",
            "sorting_order",
            "slug",
            "is_featured",
        ]



class BillItemForm(BaseForm, forms.ModelForm):
    class Meta:
        model = BillItem
        fields = [
            "product_title",
            "product_quantity",
            "rate",
            "amount",
        ]


BillItemFormset = formset_factory(
    BillItemForm,
    extra=1,
)


from .models import TblTaxEntry


class TblTaxEntryForm(BaseForm, forms.ModelForm):
    class Meta:
        model = TblTaxEntry
        fields = "__all__"
        exclude = [
            "is_deleted",
            "status",
            "deleted_at",
        ]


from .models import TblSalesEntry


class TblSalesEntryForm(BaseForm, forms.ModelForm):
    class Meta:
        model = TblSalesEntry
        fields = "__all__"


from .models import TablReturnEntry


class TablReturnEntryForm(BaseForm, forms.ModelForm):
    class Meta:
        model = TablReturnEntry
        fields = "__all__"
