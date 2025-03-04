from django.db import models
from root.utils import BaseModel
from user.models import Customer
from django.db.models.signals import post_save
from organization.models import Branch


class ProductCategory(BaseModel):
    CATEGORY_CHOICES = (
        ("FOOD", "FOOD"),
        ("BEVERAGE", "BEVERAGE"),
        ("OTHERS", "OTHERS")
    )
    title = models.CharField(max_length=255, choices=CATEGORY_CHOICES, default="FOOD", verbose_name="Product Type", unique=True)
    slug = models.SlugField(unique=True, verbose_name="Category Slug")
    description = models.TextField(
        verbose_name="Description", null=True, blank=True
    )

    def __str__(self):
        return self.title


class Product(BaseModel):
    title = models.CharField(max_length=255, verbose_name="Item Name", unique=True)
    slug = models.SlugField(unique=False, verbose_name="Item Slug")
    description = models.TextField(
        null=True, blank=True, verbose_name="Item Description"
    )
    unit = models.CharField(null=True, max_length=100, blank=True)
    
    is_taxable = models.BooleanField(default=True)
    cost_price = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    image = models.ImageField(upload_to="product/images/", null=True, blank=True)
    type = models.ForeignKey(
        ProductCategory, on_delete=models.PROTECT, null=False, blank=False
    )
    group = models.CharField(max_length=20)
    product_id = models.CharField(max_length=255, blank=True, null=True)
    barcode = models.CharField(null=True, max_length=100, blank=True)
    is_produced = models.BooleanField(default=False)
    reconcile = models.BooleanField(default=False)
    is_billing_item = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.price = round(self.price, 2)
        return super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.title} - Rs. {self.price} per {self.unit}"


class ProductRecipie(BaseModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    items = models.JSONField()

    def __str__(self):
        return f'Recipies for {self.product.title}'


class RecipieItemSale(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.SmallIntegerField()
    transaction_date = models.DateField(auto_now_add=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return 'Recipie item sale'

class ProductStock(BaseModel):
    product = models.OneToOneField(Product, on_delete=models.PROTECT)
    stock_quantity = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f'{self.product.title} -> {self.stock_quantity}'

''' Signal to create ProductStock after Product instance is created '''


def create_stock(sender, instance, created, **kwargs):
    try:
        if not ProductStock.objects.filter(product=instance).exists() and created:
            ProductStock.objects.create(product=instance)
    except Exception as e:
        print(e)

post_save.connect(create_stock, sender=Product)


"""  ***********************  """



from django.contrib.auth import get_user_model

User = get_user_model()
class ProductMultiprice(models.Model):
    product_id = models.BigIntegerField()
    product_price = models.CharField(max_length=15)
    
    class Meta:
        managed = False
        db_table = 'product_multiprice'
    
    def __str__(self):
        return f"{self.product_id}- {self.product_price}"



class CustomerProduct(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    price = models.FloatField(default=0.0)
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.product.title} - Rs. {self.price}"


class BranchStockTracking(BaseModel):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    date = models.DateField()
    opening = models.IntegerField(default=0)
    received = models.IntegerField(default=0)
    wastage = models.IntegerField(default=0)
    returned = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)
    closing = models.IntegerField(default=0)
    physical = models.IntegerField(default=0)
    discrepancy = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.title}"
    
    class Meta:
        unique_together = "branch", "product", "date"


class BranchStock(BaseModel):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.product.title} to {self.branch.name}'
    
    def save(self, *args, **kwargs):
        if ProductStock.objects.filter(product=self.product).exists():
            product = ProductStock.objects.get(product=self.product)
            product.stock_quantity -= self.quantity
            product.save()
        return super().save(*args, **kwargs)
    

class ItemReconcilationApiItem(BaseModel):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    date = models.DateField()
    wastage = models.IntegerField(default=0)
    returned = models.IntegerField(default=0)
    physical = models.IntegerField(default=0)
    terminal = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.product.title} -> {self.branch.name}"
    
    class Meta:
        unique_together = 'branch', 'product', 'date', 'terminal'


