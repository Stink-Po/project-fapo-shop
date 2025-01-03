from django.contrib import admin
from .models import PostCategory, Post, PostComment, PostSection


class PostSectionInline(admin.TabularInline):  # or admin.StackedInline
    model = PostSection
    extra = 1

# Admin model for PostCategory
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ['name']

# Admin model for Post
class PostAdmin(admin.ModelAdmin):
    inlines = [PostSectionInline]
    list_display = ('title', 'author', 'category', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author', 'category')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-publish']
    date_hierarchy = 'publish'
    autocomplete_fields = ['author', 'category']  # Makes foreign key selection easier

    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'slug', 'author', 'category', 'body', 'tags', 'image')
        }),
        ('Publishing', {
            'fields': ('status', 'publish')
        }),
        ('Important dates', {
            'fields': ('created', 'update')
        }),
    )
    readonly_fields = ('created', 'update')  # Makes these fields read-only in the admin interface

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('user__phone_number', 'body')

admin.site.register(PostComment, CommentAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)
admin.site.register(Post, PostAdmin)

