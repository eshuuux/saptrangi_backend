from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_migrations WHERE app='products';")
        print("Migration history for 'products' deleted.")
