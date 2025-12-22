from django.db import models
from users.models import User, Address
from products.models import Product


# ==================================================
# 🛒 CART
# ==================================================
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    size = models.CharField(max_length=10, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart"
        unique_together = ("user", "product", "size")
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user.id} - {self.product.name} ({self.size})"


# ==================================================
# 📦 ORDER
# ==================================================
class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("SHIPPED", "Shipped"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    total_amount = models.FloatField()
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders"
        ordering = ["-id"]

    def __str__(self):
        return f"Order #{self.id} ({self.status})"


# ==================================================
# 🧾 ORDER ITEMS
# ==================================================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()  # snapshot price

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"{self.order.id} - {self.product.name}"
