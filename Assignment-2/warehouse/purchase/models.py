from django.db import models
from inventory.models import Item

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

class PurchaseHeader(BaseModel):
    code = models.CharField(max_length=20, unique=True)
    date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return f"Purchase {self.code}"

class PurchaseDetail(BaseModel):
    header = models.ForeignKey(PurchaseHeader, on_delete=models.CASCADE, related_name='details')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.pk: 
            self.item.stock += self.quantity
            self.item.balance += self.quantity * self.unit_price
            self.item.save()
        super().save(*args, **kwargs)
