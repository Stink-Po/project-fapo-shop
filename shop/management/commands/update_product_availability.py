from django.core.management.base import BaseCommand
from shop.models import Product


class Command(BaseCommand):
    help = 'Check product colors quantity and mark product as unavailable if all colors have zero quantity'

    def handle(self, *args, **kwargs):
        # Get all products
        products = Product.objects.all()

        # Loop through each product
        for product in products:
            # Get the total quantity of all colors for this product
            total_quantity = sum(color.quantity for color in product.colors.all())

            # If total quantity is 0, mark the product as unavailable
            if total_quantity == 0:
                if product.available:
                    product.available = False
                    product.save()
                    self.stdout.write(self.style.SUCCESS(f'Product "{product.name}" marked as unavailable.'))

            # If there is any stock, mark the product as available
            else:
                if not product.available:
                    product.available = True
                    product.save()
                    self.stdout.write(self.style.SUCCESS(f'Product "{product.name}" marked as available.'))

        self.stdout.write(self.style.SUCCESS('Product availability check complete.'))
