from django.db import models

class DeliveryPincode(models.Model):
    pincode = models.CharField(max_length=6, unique=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "delivery_pincodes"

    def __str__(self):
        return self.pincode
