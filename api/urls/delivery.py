# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.delivery import DeliveryHistoryViewSet, DeliveryDetailsViewSet, DeliveryHistoryAPIView, DeliveryHistoryDateAPIView, DeleteDeliveryHistory

router = DefaultRouter()
router.register(r'delivery-history', DeliveryHistoryViewSet)
router.register(r'delivery-details', DeliveryDetailsViewSet)

# urlpatterns = [
#     path('api/', include(router.urls)),
# ]

urlpatterns = [
    path('details-deliveryhistory/', DeliveryHistoryAPIView.as_view(), name='delivery_history_api'),
        path('delivery-history-date/<str:date>/', DeliveryHistoryDateAPIView.as_view(), name='delivery-history'),
        path('delete_delivery_history/<int:delivery_id>/', DeleteDeliveryHistory.as_view(), name='delete_delivery_history'),

    ] + router.urls
