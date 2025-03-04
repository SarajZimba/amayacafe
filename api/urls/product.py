from api.views.product import CustomerProductAPI, ProductList, ProductDetail,ProductMultipriceapi, ProductTypeListView,\
    bulk_product_requisition, BranchStockTrackingView, ApiItemReconcilationView, CheckAllowReconcilationView
from django.urls import path

from rest_framework import routers

router = routers.DefaultRouter()
router.register("customer-product-list", CustomerProductAPI)

urlpatterns = [
    path('category-list/', ProductTypeListView.as_view(), name="api_category_list"),
    path("product-list/", ProductList.as_view(), name="api_product_list"),
    path("product-detail/<int:pk>", ProductDetail.as_view(), name="api_product_detail"), 
    path("product-prices/", ProductMultipriceapi.as_view(), name="api_product_price"), 
    path("product-reconcile/", BranchStockTrackingView.as_view(), name="api_product_reconcile"), 
    path("bulk-product-reconcilation/", ApiItemReconcilationView.as_view(), name="api_bulk_product_reconcile"), 
    path("bulk-requisition/", bulk_product_requisition, name="api_bulk_product_requisition"),
    path("check-reconcilation/", CheckAllowReconcilationView.as_view(), name="api_check_reconcilation"),
] + router.urls

