from django.contrib import admin
from .models import ProductCategory, Product, CustomerProduct, ProductRecipie

admin.site.register([ProductCategory, Product , CustomerProduct])
admin.site.register(ProductRecipie)
