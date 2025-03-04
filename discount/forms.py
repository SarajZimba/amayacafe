from django import forms
from root.forms import BaseForm

from discount.models import DiscountTable

class DiscountTableForm(BaseForm, forms.ModelForm):
    class Meta:
        model = DiscountTable
        fields = '__all__'
        exclude = ['is_deleted', 'status', 'deleted_at','discount_type', 'is_featured', 'sorting_order']
                        