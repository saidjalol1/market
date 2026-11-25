from django.db import models
from django.contrib.auth.models import User

from store.models import Products


class Check(models.Model):
    payment_type = models.CharField(max_length=10)
    sold = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checks")
    

    def overall(self):
        sum_ = sum([i.total() for i in self.check_items.all()])
        return sum_
    
    def discount(self):
        sum_discount = sum([i.discount_sum() for i in self.check_items.all()])
        return sum_discount
    
    def to_pay(self):
        result = self.overall() - self.discount()
        return result 

class CheckItem(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="items")
    amount = models.FloatField(default=1)

    checks = models.ForeignKey(Check, on_delete=models.CASCADE, related_name="check_items")
    
    def total(self):
        return self.product.sell_price * self.amount
    
    def discount_sum(self):
        active_discount = self.product.get_discount().latest("created_at").value
        return active_discount 