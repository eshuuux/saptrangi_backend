from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review


@receiver([post_save, post_delete], sender=Review)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    avg_rating = product.reviews.aggregate(
        avg=Avg("rating")
    )["avg"] or 0

    product.rating = round(avg_rating, 1)
    product.save(update_fields=["rating"])
