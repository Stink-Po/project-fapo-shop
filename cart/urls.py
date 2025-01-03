from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),
    path("add/", views.product_add_by_json, name="product_add_by_json"),
    path("quantity-chage/", views.update_quantity_by_json, name="product_quantity"),
    path("get-cart/", views.get_cart_by_json, name="get_cart_by_json"),
    path("remove/", views.cart_remove, name="cart_remove"),
    path("cart-len/", views.get_cart_len_by_json, name="cart_len"),
    path("check-code/", views.check_discount_code, name="check_discount_code"),
    path("add-discount-to-cart/", views.add_discount_to_cart, name="add_discount_to_cart"),
]
