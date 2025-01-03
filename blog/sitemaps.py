from .models import Post
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from  urllib.parse import unquote

class BlogPostsSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Post.published.all()


    def lastmod(self, obj):
        obj.update

    def location(self, obj):
        url = reverse('blog:post_detail', args=[obj.slug, obj.publish.year, obj.publish.month, obj.publish.day])
        decoded_url = unquote(url)
        return decoded_url

class BlogCommentsSitemap(Sitemap):
    changefreq = 'hourly'
    priority = 0.6

    def items(self):
        return Post.published.filter(comments__isnull=False).distinct()

    def lastmod(self, obj):
        last_comment = obj.comments.order_by('-created').first()
        return last_comment.created if last_comment else obj.updated

    def location(self, obj):
        # We use the post detail URL since comments don't have their own unique URL
        url = reverse('blog:post_detail', args=[obj.slug, obj.publish.year, obj.publish.month, obj.publish.day])
        decoded_url = unquote(url)
        return decoded_url