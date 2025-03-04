from django.db import models
from root.utils import BaseModel
class DiscountTable(BaseModel):

    discount_name = models.CharField(max_length=200)
    discount_type = models.CharField(
        max_length=200, default="PCT"
    )
    discount_amount = models.FloatField(verbose_name="Discount Percentage")

    def __str__(self) -> str:
        return self.discount_name
