from django.db import models
from root.utils import BaseModel
from product.models import Product, ProductStock
from django.db.models.signals import post_save

class Vendor(BaseModel):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100, null=True, blank=True)
    contact = models.CharField(max_length=10, null=True, blank=True)
    pan_no = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.pan_no}'


class Purchase(BaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(Product, through='ProductPurchase')
    bill_date = models.DateField(max_length=50, null=True, blank=True)
    bill_no = models.CharField(max_length=30, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=9, decimal_places=2)
    discount_percentage = models.IntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=9, decimal_places=2)
    taxable_amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    non_taxable_amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    amount_in_words = models.CharField(max_length=255)
    payment_mode = models.CharField(max_length=30)

    def __str__(self):
        return f'Purchased from {self.vendor.name} total = {self.grand_total}'

class AccountProductTracking(BaseModel):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    purchase_rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    available = models.BooleanField(default=True)
    remaining_stock = models.IntegerField()

    def __str__(self):
        return f'{self.product.title} @ {self.purchase_rate}'


class ProductPurchase(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField()
    item_total = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.product.title} X {self.quantity}'

''' Signal for Updating Product STock after Purchase '''

def update_stock(sender, instance, **kwargs):
    stock = ProductStock.objects.get(product=instance.product)
    stock.stock_quantity = stock.stock_quantity + instance.quantity
    stock.save()
    # Create Account product tracking after purchase 
    AccountProductTracking.objects.create(product=instance.product, purchase_rate=instance.rate, quantity=instance.quantity, remaining_stock=instance.quantity)
   

post_save.connect(update_stock, sender=ProductPurchase)


'''  IRD requirement models '''

class TblpurchaseEntry(models.Model):
    idtblpurchaseEntry = models.BigAutoField(primary_key=True)
    bill_date = models.CharField(null=True, max_length=20, blank=True)
    bill_no = models.CharField(max_length=30, null=True, blank=True)
    pp_no = models.CharField(null=True, max_length=20, blank=True)
    vendor_name = models.CharField(null=True, max_length=200, blank=True)
    vendor_pan = models.CharField(null=True, max_length=200, blank=True)
    item_name = models.CharField(null=True, max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(null=True, blank=True, max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    non_tax_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchase_req_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "tblpurchaseEntry"


class TblpurchaseReturn(models.Model):
    idtblpurchaseReturn = models.BigAutoField(primary_key=True)
    bill_date = models.CharField(null=True, max_length=20, blank=True)
    bill_no = models.CharField(max_length=30, null=True, blank=True)
    pp_no = models.CharField(null=True, max_length=20, blank=True)
    vendor_name = models.CharField(null=True, max_length=200, blank=True)
    vendor_pan = models.CharField(null=True, max_length=200, blank=True)
    item_name = models.CharField(null=True, max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(null=True, blank=True, max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    non_tax_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason = models.CharField(max_length=200, null=True, blank=True)
    

    class Meta:
        db_table = "tblpurchaseReturn"



class Production(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.title} x {self.quantity}'


''' Signal to create ProductStock after Product instance is created '''


def create_stock(sender, instance, **kwargs):
    try:
        stock, _ = ProductStock.objects.get_or_create(product=instance.product)
        stock.stock_quantity += instance.quantity
        stock.save()
    except Exception as e:
        print(e)

post_save.connect(create_stock, sender=Production)


"""      ***********************       """


""" Asset Models  """

class DepreciationPool(models.Model):
    label = models.CharField(max_length=3)
    percentage = models.SmallIntegerField()

    def __str__(self):
        return f'{self.label} - {self.percentage} %'

class Asset(BaseModel):
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    is_taxable = models.BooleanField(default=True)
    depreciation_pool = models.ForeignKey(DepreciationPool, on_delete=models.SET_NULL, null=True)
    asset_purchases = models.ManyToManyField('AssetPurchase', through='AssetPurchaseItem')

    def __str__(self):
        return f'{self.title}'


class AssetPurchase(BaseModel):

    PAYMENT_MODE = (
        ("Cash", "Cash"),
        ("Credit", "Credit"),
        ("Credit Card", "Credit Card"),
        ("Mobile Payment", "Mobile Payment"),
        ("Complimentary", "Complimentary"),
    )

    DISCOUNT_PERCENTAGE_CHOICES = (
        (0,0),
        (5,5),
        (10, 10),
        (20, 20),
        (30, 30),
        (40, 40),
        (50, 50),

    )

    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    assets = models.ManyToManyField(Asset, through='AssetPurchaseItem')
    bill_date = models.DateField(max_length=50, null=True, blank=True)
    bill_no = models.CharField(max_length=30, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=9, decimal_places=2)
    discount_percentage = models.IntegerField(default=0, choices=DISCOUNT_PERCENTAGE_CHOICES)
    discount_amount = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=9, decimal_places=2)
    taxable_amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    non_taxable_amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    amount_in_words = models.CharField(max_length=255)
    payment_mode = models.CharField(max_length=30, choices=PAYMENT_MODE)

    def __str__(self):
        return 'Asset Purchased'


class AssetPurchaseItem(BaseModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    asset_purchase = models.ForeignKey(AssetPurchase, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField()
    item_total = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.asset.title} X {self.quantity}'




