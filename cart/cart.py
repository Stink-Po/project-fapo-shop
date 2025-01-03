from django.conf import settings
from shop.models import Product, ProductColor
from django.shortcuts import get_object_or_404
from django.utils import timezone

class Cart:
    def __init__(self, request_or_session_data):
        if hasattr(request_or_session_data, 'session'):  # Check if it's a request
            self.session = request_or_session_data.session
        else:
            # If it's session data, use it directly
            self.session = request_or_session_data
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.total_discount = None
        self.discount_code = self.session.get("discount_code", None)
        self.have_discount_code = self.session.get("have_discount_code", False)
        self.discount_code_amount = self.session.get("discount_code_amount", 0)
        self.last_updated = self.session.get("last_updated")
        if hasattr(request_or_session_data, 'user') and request_or_session_data.user.is_authenticated:
            self.user = request_or_session_data.user



    def add(self, product, color_id, quantity=1, override_quantity=False):
        product_id = str(product.id)
        color = get_object_or_404(ProductColor, id=color_id)
        cart_key = f"{product_id}_{color_id}"

        if cart_key not in self.cart:
            self.cart[cart_key] = {
                'color_id': str(color.id),
                'quantity': 0,
                'price': str(product.price),
                'discount': str(product.discount),
                'discount_price': str(product.get_discounted_price()),
            }

        if override_quantity:
            self.cart[cart_key]['quantity'] = quantity
        else:
            self.cart[cart_key]['quantity'] += quantity

        self.total_discount = self.get_total_discount()
        self.save()

    def mark_session_modified(self):
        # Mark session as modified if `self.session` is a Django session object
        if hasattr(self.session, 'modified'):
            self.session.modified = True

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.last_updated = timezone.now()
        self.session[settings.CART_SESSION_ID] = self.cart
        self.discount_code = self.session.get('discount_code', None)
        self.have_discount_code = self.session.get('have_discount_code', None)
        self.session['discount_code_amount'] = self.discount_code_amount
        self.session['last_updated'] = self.last_updated.isoformat()
        if hasattr(self, 'user') and self.user:
            self.session["user_id"] = self.user.id
        self.mark_session_modified()

    def remove(self, product, color_id=None):
        product_id = str(product.id)
        if color_id:
            cart_key = f"{product_id}_{color_id}"
            if cart_key in self.cart:
                del self.cart[cart_key]
        else:
            # If no color_id is provided, remove all items related to the product_id
            keys_to_remove = [key for key in self.cart if key.startswith(product_id)]
            for key in keys_to_remove:
                del self.cart[key]

        if len(self.cart) == 0:
            self.clear()  # Call the clear method to remove discount codes and other data

        else:
            self.total_discount = self.get_total_discount()  # Update total discount
            self.save()

    def __iter__(self):
        cart = self.cart.copy()
        product_ids = {key.split('_')[0] for key in cart.keys()}  # Extract product IDs
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            for key in cart.keys():
                if key.startswith(str(product.id)):
                    item = cart[key]
                    item["product"] = product.id
                    item["name"] = product.name
                    item["image"] = product.images.all()[0].image.url

                    # Extract color ID from the key
                    color_id = key.split('_')[1] if '_' in key else None

                    # Get the corresponding ProductColor instance
                    if color_id:
                        try:
                            product_color = ProductColor.objects.get(id=color_id, product=product)
                            item["color_name"] = product_color.color  # Use the color from ColorChoices
                            item["color"] = product_color.get_color_display()
                        except ProductColor.DoesNotExist:
                            item["color_name"] = "Unknown Color"
                            item["color"] = None
                    else:
                        item["color_name"] = "No Color"

                    item["color_id"] = str(color_id)
                    item["product_id"] = str(product.id)
                    item["price"] = int(item["price"])
                    item["discount_price"] = int(item["discount_price"])
                    if item["discount"] == "0":
                        item["total_price"] = item["price"] * item["quantity"]
                    else:
                        item["total_price"] = item["discount_price"] * item["quantity"]

                    yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        total_price = 0
        for item in self:
            total_price += item["total_price"]
        if self.have_discount_code:
            discount_factor = self.discount_code_amount / 100
            total_price = int(total_price * (1 - discount_factor))
        return total_price

    def get_cart_price_without_discount(self):
        total = 0
        for item in self:
            total += item["price"] * item["quantity"]
        return total

    def add_coupon(self, amount, code):
        self.discount_code_amount = amount
        self.have_discount_code = True
        self.discount_code = code
        self.save()

    def get_total_discount(self):
        total_discount = 0
        for item in self.cart.values():
            if item["discount"] != "0":
                discount = int(item["price"]) - int(item["discount_price"])
                total_discount += discount * item["quantity"]
        return total_discount

    @property
    def total_get_price_of_discount(self):
        total_price = 0
        for item in self:
            total_price += item["total_price"]
        price = self.get_total_price()

        return total_price - price

    def clear(self):
        # remove cart from session

        keys_to_remove = [
            settings.CART_SESSION_ID,
            'have_discount_code',
            'discount_code_amount',
            'discount_code',
            'last_updated',
            'sms_sent'
        ]
        for key in keys_to_remove:
            self.session.pop(key, None)

        self.mark_session_modified()


