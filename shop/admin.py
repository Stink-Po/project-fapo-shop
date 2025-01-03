from django.contrib import admin
from .models import Category, Product, ProductImage, ProductColor, Comment, ProductsScore, ProductFeatures
from django.utils.text import slugify
from django import forms


# Inline admin class for ProductImage (multiple images per product)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty fields to show initially
    fields = ['image', 'image_alt']


# Inline admin class for ProductColor (multiple colors per product)
class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1  # Number of empty fields to show initially
    fields = ['color', 'quantity']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'color':
            # Show color names in the dropdown while using hex codes as values
            kwargs['widget'] = forms.Select(choices=[
                (color_choice[0], color_choice[1]) for color_choice in ProductColor.ColorChoices.choices
            ])
        return super().formfield_for_dbfield(db_field, request, **kwargs)


# Inline admin class for Comment (comments related to products)
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ['user', 'text', 'score']


# Inline admin class for ProductsScore (scores related to products)
class ProductsScoreInline(admin.TabularInline):
    model = ProductsScore
    extra = 1
    fields = ['user', 'score']


class ProductFeaturesInline(admin.TabularInline):
    model = ProductFeatures
    extra = 1  # Start with one empty form for adding a feature
    fields = ['dishwasher', 'owen', 'microwave', 'flame', 'height', 'width', 'diameter', 'material', 'capacity',
              'country_of_origin', 'weight']
    verbose_name_plural = 'Product Features'


# Admin class for Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_numbers']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    ordering = ['name']

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name, allow_unicode=True)

        if not obj.image_alt:  # Automatically generate image_alt from the name if not provided
            obj.image_alt = f" تصویر {obj.name} "

        super().save_model(request, obj, form, change)


# Admin class for Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'available', 'created', 'updated', 'get_discounted_price',
                    'get_comment_count', 'get_total_score']
    list_filter = ['available', 'category', 'created', 'updated']
    search_fields = ['name', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductColorInline, CommentInline, ProductsScoreInline, ProductFeaturesInline]
    ordering = ['name']
    readonly_fields = ['get_discounted_price', 'get_comment_count', 'get_total_score']


# Admin class for ProductImage (if you want a separate admin interface for product images)
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_alt']
    search_fields = ['product__name']

    def save_model(self, request, obj, form, change):
        if not obj.image_alt:
            obj.image_alt = f" تصویر {obj.product.name}"

        super().save_model(request, obj, form, change)


# Admin class for ProductColor (if you want a separate admin interface for product colors)
class ProductColorAdminForm(forms.ModelForm):
    class Meta:
        model = ProductColor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show color names (labels) in the dropdown while using hex codes (values)
        self.fields['color'].choices = [
            (color_choice[0], color_choice[1]) for color_choice in ProductColor.ColorChoices.choices
        ]


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    form = ProductColorAdminForm
    list_display = ['product', 'get_color_name', 'quantity']

    def get_color_name(self, obj):
        # Get the color name (label) based on the color value
        return dict(ProductColor.ColorChoices.choices).get(obj.color, obj.color)

    get_color_name.short_description = "Color"


# Admin class for Comment (if you want a separate admin interface for comments)
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'text', 'score', 'created_at']
    list_filter = ['created_at', 'score']
    search_fields = ['product__name', ]


# Admin class for ProductsScore (if you want a separate admin interface for scores)
@admin.register(ProductsScore)
class ProductsScoreAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['product__name', ]
