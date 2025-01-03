from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from  urllib.parse import unquote

class StaticAccountsView(Sitemap):
    protocol = "https"
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ["accounts:login"]

    def location(self, item):
        url = reverse(item)
        decoded_url = unquote(url)  # Decode the URL-encoded string
        return decoded_url
