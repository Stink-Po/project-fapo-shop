import decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from PIL import Image, ImageOps, ImageDraw
import os
from django.conf import settings
import random
from django.db.models import Sum
from io import BytesIO
from django.core.files.base import ContentFile

# User model
User = get_user_model()


# Category model
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/')
    image_alt = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"])
        ]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def product_numbers(self):
        return self.products.count()

    def get_absolute_url(self):
        return reverse("shop:product_list_by_category", args=[self.slug])

    def save(self, *args, **kwargs):
        img = Image.open(self.image)

        # Correct rotation based on EXIF data
        img = ImageOps.exif_transpose(img)

        # Ensure the image is square by cropping from the center
        width, height = img.size
        min_side = min(width, height)
        left = (width - min_side) // 2
        top = (height - min_side) // 2
        right = left + min_side
        bottom = top + min_side
        img = img.crop((left, top, right, bottom))

        # Resize the cropped image to the desired size
        desired_size = 300
        img = img.resize((desired_size, desired_size), Image.Resampling.LANCZOS)

        # Create a circular mask
        mask = Image.new("L", (desired_size, desired_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, desired_size, desired_size), fill=255)

        # Create a white background for the circular image
        circular_image = Image.new("RGB", (desired_size, desired_size), (255, 255, 255))
        circular_image.paste(img, (0, 0), mask=mask)

        # Save the processed circular image to a BytesIO buffer
        buffer = BytesIO()
        circular_image.save(buffer, format="JPEG", quality=95)  # High quality

        # Replace the uploaded image with the processed circular image
        self.image = ContentFile(buffer.getvalue(), self.image.name)

        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)

        if not self.image_alt:
            self.image_alt = f"تصویر {self.slug}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Product model
class Product(models.Model):
    unique_id = models.CharField(max_length=8, unique=True, editable=False, null=True, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, allow_unicode=True)
    short_description = models.TextField(blank=True, null=True)
    description = models.TextField()
    price = models.PositiveIntegerField()
    cost_price = models.PositiveIntegerField(null=True, blank=True, default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    discount = models.PositiveIntegerField(default=0)
    offer_end = models.DateTimeField(blank=True, null=True)
    user_likes = models.ManyToManyField(User, related_name="product_likes", blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["-created"]),
        ]

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[self.id, self.slug])

    def get_discounted_price(self):
        if self.discount and self.discount !=0:
            discount_factor = self.discount / 100
            return int(self.price * (1 - discount_factor))
        return self.price

    def get_total_score(self):
        try:
            scores = self.score.all()
            total_score = sum(score.score for score in scores)
            return round(total_score / len(scores), 1)
        except ZeroDivisionError:
            return 0

    def get_profit(self, cart_discount=None):
        """
        Calculates the profit after all applicable discounts (product, user, and cart).
        - user_discount: The discount a user has (e.g., 10% discount on the total cart)
        - cart_discount: Any discount on the cart level
        """
        # Final selling price after product discount
        final_price = self.get_discounted_price()

        # Apply cart-level discount (on the final price after user discount)
        if cart_discount:
            print("yes discount in profit")
            final_price *= (1 - cart_discount / 100)

        # Calculate the profit: selling price minus cost price
        return final_price - self.cost_price

    def get_score_count(self):
        return self.score.count()

    def get_comment_count(self):
        return self.product_comments.count()

    def get_discounted_margin(self):
        return self.price - self.get_discounted_price()

    def save(self, *args, **kwargs):
        if not self.unique_id:
            while True:
                unique_id = f"{random.randint(10000000, 99999999)}"
                if not Product.objects.filter(unique_id=unique_id).exists():
                    self.unique_id = unique_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductFeatures(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='features',
        on_delete=models.CASCADE,
        verbose_name="محصول"
    )
    dishwasher = models.BooleanField(null=True, blank=True, verbose_name="قابل شستشو در ماشین ظرفشویی")
    owen = models.BooleanField(null=True, blank=True, verbose_name="قابل استفاده در فر")
    microwave = models.BooleanField(null=True, blank=True, verbose_name="قابل استفاده در مایکروویو")
    flame = models.BooleanField(null=True, blank=True, verbose_name="قابل استفاده روی شعله")
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name="ارتفاع")
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name="عرض")
    diameter = models.PositiveIntegerField(null=True, blank=True, verbose_name="قطر")
    material = models.CharField(max_length=50, null=True, blank=True, verbose_name="جنس")
    capacity = models.PositiveIntegerField(null=True, blank=True, verbose_name="ظرفیت")
    country_of_origin = models.CharField(max_length=50, null=True, blank=True, verbose_name="کشور سازنده")
    weight = models.PositiveIntegerField(null=True, blank=True, verbose_name="وزن")

    class Meta:
        verbose_name = "ویژگی محصول"
        verbose_name_plural = "ویژگی‌های محصول"

    def non_empty_fields(self):
        fields = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if value is not None:  # Check for non-empty values
                if isinstance(value, bool):  # Handle Boolean fields
                    fields[field.verbose_name] = "بله" if value else "خیر"
                elif isinstance(value, (int, float, decimal.Decimal)):  # Handle numeric fields with units
                    if field.name in ["diameter", "height", "width"] :
                        unit = "سانتی متر"
                    elif field.name == "weight":
                        unit = "گرم"
                    elif field.name == "capacity":
                        unit = " سی سی"
                    else:
                        unit = ""
                    fields[field.verbose_name] = f"{value} {unit}"
                else:  # Handle other fields normally
                    fields[field.verbose_name] = value
        return fields

    def ret_futures(self):
        return self.non_empty_fields()



# Product Image model (for multiple images per product)
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    image_alt = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.image_alt:
            self.image_alt = f"تصویر {self.product.name}"

        logo_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'image', 'logo.png')
        if not os.path.exists(logo_path):
            raise FileNotFoundError(f"Logo file not found at {logo_path}")

        image_path = self.image.path

        # Open the main image
        img = Image.open(image_path).convert("RGBA")

        # Resize the image proportionally to fit within 800x800
        target_size = (1200, 1200)
        img = ImageOps.fit(img, target_size, Image.Resampling.LANCZOS)

        # Open the logo image
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = (150, 150)
        logo.thumbnail(logo_size, Image.Resampling.LANCZOS)

        # Calculate the logo position: bottom-right corner with padding
        padding = 20
        logo_position = (
            target_size[0] - logo.width - padding,
            target_size[1] - logo.height - padding,
        )

        # Paste the logo onto the image
        img.paste(logo, logo_position, logo)

        # Convert RGBA to RGB for JPEG compatibility
        if image_path.lower().endswith(('.jpg', '.jpeg')):
            img = img.convert("RGB")

        # Save the final image
        img.save(image_path)


class ProductsScore(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="score")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score by {self.user.id} on {self.product.name}"

    @classmethod
    def get_total_score(cls, product_id):
        try:
            scores = cls.objects.filter(product_id=product_id)
            total_score = sum(score.score for score in scores)
            return round(total_score / len(scores), 1)
        except ZeroDivisionError:
            pass

        return 0

# Product Color model (for multiple colors with separate quantities)
class ProductColor(models.Model):
    class ColorChoices(models.TextChoices):
        RED = "#f50b0b","قرمز"
        BLUE = "#0844f3","آبی"
        YELLOW ="#f7f704", "زرد"
        GREEN = "#22f704","سبز"
        PINK = "#f704e8","صورتی"
        PURPLE = "#901f89","بنفش"
        GRAY = "#9c939c","خاکستری"
        WHITE = "#ffffff","سفید"
        BLACK = "#000000","سیاه"
        ORANGE = "#f2780c","نارنجی"
        BROWN =  "#513924","قهوه ای"
        GLASS = "#f3f3f2", "شیشه ای"
        RAINBOW = "##FF66CC", "چند رنگ"

    product = models.ForeignKey(Product, related_name='colors', on_delete=models.CASCADE)
    color = models.CharField(choices=ColorChoices.choices, max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)  # New field for reserved items

    def available_quantity(self):
        return self.quantity - self.reserved_quantity


    def __str__(self):
        return f"{self.product.name} - {self.color}"


# Comment model (for users to comment on products)
class Comment(models.Model):
    product = models.ForeignKey(Product, related_name='product_comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='product_comments', on_delete=models.CASCADE)
    text = models.TextField()
    score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.product.name}"


class ProductsProfit(models.Model):
    total_invest = models.PositiveIntegerField(default=0)
    profit = models.PositiveIntegerField(default=0)
    sell_prices = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        total = Product.objects.aggregate(total_cost=Sum('cost_price'))['total_cost'] or 0
        self.total_invest = total

        super().save(*args, **kwargs)


