from django.db import models
from users.models import User, Address
from products.models import Product



# ===================================================================
# 🛒 CART TABLE — Temporary storage before checkout
# ===================================================================
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)        # faster lookup
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)  # speed on joins
    quantity = models.PositiveIntegerField(default=1)  # Prevent negative values
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart"
        unique_together = ("user", "product")   # avoid duplicates

    def __str__(self):
        return f"{self.user.mobile} - {self.product.name} ({self.quantity})"



# ===================================================================
# 📦 ORDER MASTER TABLE — Main Order header
# ===================================================================
class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Shipped", "Shipped"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    total_amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "orders"
        ordering = ["-id"]       # latest orders first

    def __str__(self):
        return f"Order #{self.id} - {self.user.mobile}"



# ===================================================================
# 🧾 ORDER ITEMS — Every product stored inside an order
# ===================================================================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField()  # snapshot price at time of order

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"{self.order.id} - {self.product.name}"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    razorpay_order_id = models.CharField(max_length=200)
    razorpay_payment_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"

    def __str__(self):
        return f"Payment for Order {self.order.id}"
