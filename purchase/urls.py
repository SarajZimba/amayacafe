from django.urls import path

from .views import VendorList,VendorDetail,VendorCreate,VendorUpdate,VendorDelete

urlpatterns = [
    path('vendor/', VendorList.as_view(), name='vendor_list'),
    path('vendor/<int:pk>/', VendorDetail.as_view(), name='vendor_detail'),
    path('vendor/create/', VendorCreate.as_view(), name='vendor_create'),
    path('vendor/<int:pk>/update/', VendorUpdate.as_view(), name='vendor_update'),
    path('vendor/delete', VendorDelete.as_view(), name='vendor_delete'),
]


from .views import ProductPurchaseCreateView, PurchaseListView, PurchaseDetailView, MarkPurchaseVoid, PurchaseBookListView, VendorWisePurchaseView

urlpatterns += [
    path('purchase/create/', ProductPurchaseCreateView.as_view(), name="product_purchase_create"),
    path('purchase/<int:pk>/', PurchaseDetailView.as_view(), name="purchase_detail"),
    path('purchase/void/<int:pk>', MarkPurchaseVoid.as_view(), name="purchase_void"),
    path('purchase/', PurchaseListView.as_view(), name="purchase_list"),
    path('pb/', PurchaseBookListView.as_view(), name="purchase_book_list"),
    path('vwp/', VendorWisePurchaseView.as_view(), name="vendor_wise_purchase"),

]

from .views import AssetPurchaseList,AssetPurchaseDetail,AssetPurchaseCreate,AssetPurchaseUpdate#,AssetPurchaseDelete
urlpatterns += [
path('asset/', AssetPurchaseList.as_view(), name='assetpurchase_list'),
path('asset/<int:pk>/', AssetPurchaseDetail.as_view(), name='assetpurchase_detail'),
path('asset/create/', AssetPurchaseCreate.as_view(), name='assetpurchase_create'),
path('asset/<int:pk>/update/', AssetPurchaseUpdate.as_view(), name='assetpurchase_update'),
# path('asset/delete', AssetPurchaseDelete.as_view(), name='assetpurchase_delete'),
]

from .views import ProductionList,ProductionDetail,ProductionCreate,ProductionUpdate,ProductionDelete
urlpatterns += [
path('prdctn/', ProductionList.as_view(), name='production_list'),
path('prdctn/<int:pk>/', ProductionDetail.as_view(), name='production_detail'),
path('prdctn/create/', ProductionCreate.as_view(), name='production_create'),
path('prdctn/<int:pk>/update/', ProductionUpdate.as_view(), name='production_update'),
path('prdctn/delete', ProductionDelete.as_view(), name='production_delete'),
]







