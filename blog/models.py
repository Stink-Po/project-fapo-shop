from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from django.urls import reverse
from taggit.managers import TaggableManager
from django.utils.text import slugify



class PostCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    icon = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"])
        ]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def get_absolute_url(self):
        return reverse("blog:post_by_categories", args=[self.slug, self.id])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    category = models.ForeignKey(PostCategory, related_name="posts", on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date="publish", allow_unicode=True)
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name="blog_posts")
    body = models.TextField()
    tags = TaggableManager()
    image = models.ImageField(upload_to="post_images", null=True, blank=True)
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)

    objects = models.Manager()  # The Default Manager
    published = PublishedManager()  # Our Custom Manager

    class Meta:
        ordering = ["-publish"]
        indexes = models.Index(fields=["-publish"]),

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[
            self.slug,
            self.publish.year,
            self.publish.month,
            self.publish.day,

        ])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)

        super().save(*args, **kwargs)

class PostSection(models.Model):
    post = models.ForeignKey(Post, related_name="sections", on_delete=models.CASCADE)
    subtitle = models.CharField(max_length=250)
    image = models.ImageField(upload_to="post_section_images", null=True, blank=True)
    body = models.TextField()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Section: {self.subtitle} (Post: {self.post.title})"

class PostComment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)

    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.user} on {self.post}'

    @property
    def is_reply(self):
        """Return True if the comment is a reply to another comment."""
        return self.parent is not None
