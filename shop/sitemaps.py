from django.contrib.sitemaps import Sitemap
from .models import Category, Product
from  urllib.parse import unquote


class CategorySitemap(Sitemap):
    protocol = "https"
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        url = obj.get_absolute_url()
        decoded_url = unquote(url)
        return decoded_url

class ProductSitemap(Sitemap):
    protocol = "https"
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Product.objects.filter(available=True)

    def lastmod(self, obj):
        return obj.updated

    def location(self, obj):
        url = obj.get_absolute_url()
        decoded_url = unquote(url)
        return decoded_url

    def changefreq(self, obj):
        return "daily"

    def priority(self, obj):
        return 0.8


