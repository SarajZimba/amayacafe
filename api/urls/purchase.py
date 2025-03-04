from django.urls import path
from api.views.purchase import create_bulk_production


urlpatterns = [
    path('bulk-production/', create_bulk_production, name="create_bulk_production"),
] 
