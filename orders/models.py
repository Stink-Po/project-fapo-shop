from django.db import models
from shop.models import Product, ProductColor
from accounts.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()


class Order(models.Model):
    class OrderChoices(models.TextChoices):
        SEND = "Send", "ارسال شده"
        PROCESSIONING = "Processing", "درحال پردازش"
        FAIL = "Fail", "ناموفق"

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='orders', null=True,
                             blank=True)  # remove null and blank later
    status = models.CharField(max_length=10, choices=OrderChoices.choices, default=OrderChoices.PROCESSIONING)
    track_id = models.CharField(max_length=30, null=True,blank=True)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    phone = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=250, null=True)
    email = models.EmailField(blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    province = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    discount_code = models.CharField(max_length=35, blank=True, null=True)
    post_follow_up = models.CharField(max_length=100, blank=True, null=True)
    discount_amount = models.PositiveIntegerField(default=0)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"])
        ]

    def __str__(self):
        return f"Order {self.id}"

    def get_total_cost(self):
        total_cost = sum(item.get_cost() for item in self.items.all())
        discount_factor = self.discount_amount / 100
        if self.discount_code:
            total_cost = int(total_cost * (1 - discount_factor))
        return int(total_cost)


class OrderItem(models.Model):
    color_obj = models.ForeignKey(ProductColor, related_name="order_items", on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, related_name="items", on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.SET_NULL, null=True, blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)
    price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)
    discount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        if int(self.discount) != 0:
            discount_factor = self.discount / 100
            return (self.price * self.quantity) * (1 - discount_factor)
        return self.price * self.quantity



class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True , related_name="payment")
    order =models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="payment")
    timestamp = models.DateTimeField(null=True, blank=True)
    card_number = models.CharField(max_length=50,null=True, blank=True)
    status = models.CharField(max_length=150,null=True, blank=True)
    amount = models.PositiveIntegerField(default=0, null=True, blank=True)
    track_id = models.CharField(max_length=30, null=True, blank=True)
    ref_number = models.CharField(max_length=150,null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    result = models.CharField(max_length=250, null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
