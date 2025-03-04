from discount.models import DiscountTable
from rest_framework.serializers import ModelSerializer


class DiscountSerilizer(ModelSerializer):
    class Meta:
        model = DiscountTable
        fields = 'id', 'discount_name', 'discount_type', 'discount_amount'
