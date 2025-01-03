from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.default_shop_view, name="shop"),
    path("like/", views.product_like, name="like_product"),
    path("category/", views.product_filter_by_categories , name="category"),
    path("product_detail/<int:product_id>/<str:product_slug>/", views.product_detail, name="product_detail"),
    path("check-stock/", views.quantity_of_product_with_color, name="check_stock"),
    path("search/", views.product_search, name="search"),
    path("category/<str:slug>/", views.category, name="product_list_by_category",)
]
