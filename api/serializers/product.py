from unicodedata import category
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from organization.models import EndDayDailyReport

from product.models import CustomerProduct, Product, ProductCategory,ProductMultiprice, BranchStockTracking, ItemReconcilationApiItem


class ProductMultipriceSerializer(ModelSerializer):
    class Meta:
        model = ProductMultiprice


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "image",
            "price",
            "is_taxable",
            "product_id",
            "unit",
            "barcode",
            "group",
            "reconcile"
        ]


class ProductCategorySerializer(ModelSerializer):
    items = ProductSerializer(read_only=True, many=True, source="product_set" )
    class Meta:
        model = ProductCategory
        fields = ["id", "title", "slug", "description", "items"]


class CustomerProductSerializer(ModelSerializer):
    class Meta:
        model = CustomerProduct
        fields = [
            "product",
            "customer",
            "price",
        ]


class PriceLessProductSerializer(ModelSerializer):
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "image",
            "is_taxable",
            "product_id",
            "unit",
            "category",
        ]


class CustomerProductDetailSerializer(ModelSerializer):
    product = PriceLessProductSerializer()
    agent = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = CustomerProduct
        fields = [
            "product",
            "price",
            "customer",
            "agent",
        ]

        optional_fields = ["agent"]

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        product_representation = representation.pop("product")
        for key in product_representation:
            representation[key] = product_representation[key]

        return representation

    def to_internal_value(self, data):
        product_internal = {}
        for key in PriceLessProductSerializer.Meta.fields:
            if key in data:
                product_internal[key] = data.pop(key)
        internal = super().to_internal_value(data)
        internal["product"] = product_internal
        return internal


class BranchStockTrackingSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=True)
    class Meta:
        model = BranchStockTracking
        fields = "branch", "product", 'wastage', 'returned', 'physical', 'date'


class ProductReconcileSerializer(serializers.Serializer):
    products = BranchStockTrackingSerializer(many=True)


class EndDayDailyReportSerializer(ModelSerializer):
    class Meta:
        model = EndDayDailyReport
        exclude = [
            'created_at', 'updated_at', 'status', 'is_deleted', 'sorting_order', 'is_featured'
        ]

class ItemReconcilationApiItemSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=True)
    class Meta:
        model = ItemReconcilationApiItem
        fields = 'branch', 'product', 'date', 'wastage', 'returned', 'physical',

class BulkItemReconcilationApiItemSerializer(serializers.Serializer):
    items = ItemReconcilationApiItemSerializer(many=True)
    terminal = serializers.CharField(max_length=20, required=True)
    branch = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)
    report_total = EndDayDailyReportSerializer()
    
    def create(self, validated_data):
        items = validated_data.get('items', [])
        for item in items:
            ItemReconcilationApiItem.objects.create(**item)
        return validated_data
