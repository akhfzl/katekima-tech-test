from django.db import models
from inventory.models import Item

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

class SellHeader(BaseModel):
    code = models.CharField(max_length=20, unique=True)
    date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return f"Sell {self.code}"


class SellDetail(BaseModel):
    header = models.ForeignKey(SellHeader, on_delete=models.CASCADE, related_name='details')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.quantity > self.item.stock:
                raise ValueError("Insufficient stock")

            avg_price = 0
            if self.item.stock > 0:
                avg_price = self.item.balance // self.item.stock
            self.item.stock -= self.quantity
            self.item.balance -= self.quantity * avg_price
            self.item.save()

        super().save(*args, **kwargs)

