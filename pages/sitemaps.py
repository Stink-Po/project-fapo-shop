from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from  urllib.parse import unquote

class PagesSiteMap(Sitemap):
    protocol = "https"
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return [
            "pages:index",
            "pages:contact",
            "pages:privacy_policy",
            "pages:frequency_asked_questions",
            "pages:about_us",
            "pages:terms",
        ]


    def location(self, item):
        url = reverse(item)
        decoded_url = unquote(url)
        return decoded_url
