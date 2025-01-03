from django.contrib.sitemaps import Sitemap
from .models import Offer
from  urllib.parse import unquote
from django.urls import reverse


class OffersSitemap(Sitemap):
    protocol = "https"
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Offer.objects.all()

    def lastmod(self, obj):
        obj.start_date

    def location(self, obj):
        url = reverse("offers:offer_detail" , kwargs={'offer_id': obj.id})
        decoded_url = unquote(url)  # Decode the URL-encoded string
        return decoded_url
