from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from accounts.sitemaps import StaticAccountsView
from blog.sitemaps import BlogPostsSitemap, BlogCommentsSitemap
from shop.sitemaps import CategorySitemap, ProductSitemap
from offers.sitemaps import OffersSitemap
from pages.sitemaps import PagesSiteMap
sitemaps = {
    "blog_posts": BlogPostsSitemap,
    "blog_comments": BlogCommentsSitemap,
    "accounts": StaticAccountsView,
    "shop_category": CategorySitemap,
    "products": ProductSitemap,
    "offers": OffersSitemap,
    "pages": PagesSiteMap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path("order/", include("orders.urls", namespace="orders")),  # Ensure `app_name` is set in `orders.urls`
    path("", include("pages.urls")),  # Home or general pages
    path("accounts/", include("accounts.urls", namespace="accounts")),  # Accounts app
    path("social-auth/", include("social_django.urls", namespace="social")),  # Social auth
    path("cart/", include("cart.urls", namespace="cart")),  # Shopping cart
    path("cities/", include("cities.urls", namespace="cities")),  # Cities app
    path("sms/", include("sms.urls", namespace="sms")),  # SMS app
    path("ticket/", include("tickets.urls", namespace="tickets")),  # Tickets app
    path("blog/", include("blog.urls", namespace="blog")),  # Blog app
    path("shop/", include("shop.urls", namespace="shop")),  # Shop app
    path("staff/", include("staff_area.urls", namespace="staff_area")),  # Staff area
    path("offers/", include("offers.urls", namespace="offers")),  # Offers app
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
