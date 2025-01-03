from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Category, Product, ProductColor, Comment, ProductsScore
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from .forms import SortCategoriesForm
from django.db.models import Count, Prefetch, Q
import redis
from django.conf import settings
import random
import os





r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))

def sort_products(sort_by, categories=None):
    if categories:
        products = Product.objects.filter(category__id__in=categories).order_by('-available', 'name')
    else:
        products = Product.objects.all().order_by('-available', 'name')

    products = products.prefetch_related(
        Prefetch('colors', queryset=ProductColor.objects.order_by('-quantity'))
    )
    if sort_by == 'default':
        products = products
    elif sort_by == 'favorite':
        products = products.annotate(like_count=Count('user_likes')).order_by("-available", '-like_count', )
    elif sort_by == "cheaper":
        products = products.order_by("-available", "price")
    elif sort_by == "expensive":
        products = products.order_by("-available", "-price")
    elif sort_by == "new":
        products = products.order_by("-available","-created")
    elif sort_by == "must_sell":
        products_must_sell = r.zrange("product_sell", 0, -1, desc=True)
        if products_must_sell:
            product_ids = [int(product_id) for product_id in products_must_sell]
            must_sell_products = list(Product.objects.filter(id__in=product_ids).order_by("-available"))
            must_sell_products.sort(key=lambda x: product_ids.index(x.id))
            other_products = products.exclude(id__in=product_ids).order_by("-available")
            products = must_sell_products + list(other_products)
        else:

            products = products  # edit this later

    return products




def default_shop_view(request):
    form = SortCategoriesForm()
    page = request.GET.get('page')
    sort_by = request.GET.get('sort_by')
    post_only = request.GET.get('post_only')
    if not sort_by:
        sort_by = "default"
    categories = Category.objects.all()
    products = sort_products(sort_by=sort_by)
    paginator = Paginator(products, 6)  # Show 8 posts per page
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        if post_only:
            return HttpResponse("")
        products = paginator.page(paginator.num_pages)

    context = {
        "form": form,
        "categories": categories,
        "products": products,
        "sort_by": sort_by,
    }
    if post_only:
        return render(request, "shop/producs_list.html", context)
    else:
        return render(request, "shop/base_shop.html", context)


@login_required
@require_POST
def product_like(request):
    product_id = request.POST.get('product_id')
    action = request.POST.get('action')

    if product_id and action:
        try:
            product = Product.objects.get(id=product_id)
            if action == "like":
                product.user_likes.add(request.user)
            else:
                product.user_likes.remove(request.user)

            return JsonResponse({"status": "ok"})
        except Product.DoesNotExist:
            pass

    return JsonResponse({"status": "error"})


def product_filter_by_categories(request):
    form = SortCategoriesForm()
    categories = Category.objects.all()
    selected_categories = request.GET.getlist('categories')

    if selected_categories:
        page = request.GET.get('page')
        sort_by = request.GET.get('sort_by')
        post_only = request.GET.get('post_only')

        try:
            selected_categories = [int(i) for i in selected_categories]
        except ValueError:
            selected_categories = str(selected_categories[0]).split(",")
            selected_categories = [int(i) for i in selected_categories]
        products = sort_products(sort_by=sort_by, categories=selected_categories)
        paginator = Paginator(products, 6)  # Show 8 posts per page
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            if post_only:
                return HttpResponse("")
            products = paginator.page(paginator.num_pages)

        context = {
            "categories": categories,
            "products": products,
            "sort_by": sort_by,
            "selected_categories": selected_categories,
            "form": form
        }
        if post_only:
            return render(request, "shop/producs_list.html", context)
        else:
            return render(request, "shop/prducts_with_categories.html", context)

    return redirect("shop:shop")


def product_detail(request, product_id, product_slug):
    product = get_object_or_404(Product, id=product_id, slug=product_slug)
    colors_with_stock = ProductColor.objects.filter(product=product, ).order_by('-quantity')

    product = Product.objects.prefetch_related(
        Prefetch(
            'colors',
            queryset=colors_with_stock
        )).get(id=product_id, slug=product_slug)

    r.zincrby("product_ranking", 1, product_id)

    user_score_exists = (
        ProductsScore.objects.filter(product=product, user=request.user).exists()
        if request.user.is_authenticated else False
    )
    features = product.features.first()
    product_futures = features.non_empty_fields() if features else {}

    if request.method == "POST" and request.user.is_authenticated:
        rating = request.POST.get('rating', None)
        comment_text = request.POST.get('comment', None)
        if comment_text != "" and not None:
            new_comment = Comment(product=product, user=request.user, text=comment_text, score=int(rating))
            new_comment.save()
        if rating != "" and not None:
            if not user_score_exists:
                new_score = ProductsScore(product=product, user=request.user, score=int(rating))
                new_score.save()
            else:
                this_user_score = ProductsScore.objects.filter(product=product, user=request.user).first()
                this_user_score.score = int(rating)
                this_user_score.save()

    all_products = Product.objects.exclude(id=product_id)
    discount_list = [product for product in all_products if product.discount != 0]
    random_product = random.choice(discount_list)
    random_product_colors_with_stock = ProductColor.objects.filter(product=random_product, ).order_by('-quantity')
    random_product = Product.objects.prefetch_related(
        Prefetch(
            'colors',
            queryset=random_product_colors_with_stock
        )).get(id=random_product.id, slug=random_product.slug)

    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:8]

    return render(request, "shop/product_detail.html", {
        "product": product,
        "product_futures": product_futures,
        "random_product": random_product,
        "similar_products": similar_products,
    })


def quantity_of_product_with_color(request):
    color_id = request.GET.get('color')
    try:
        product_color = ProductColor.objects.get(id=color_id)
        data = {
            'in_stock': product_color.quantity > 0,
            'quantity': product_color.quantity
        }
    except ProductColor.DoesNotExist:
        data = {
            'in_stock': False,
            'quantity': 0
        }

    return JsonResponse(data)


def product_search(request):
    query = request.GET.get("query")
    if query.startswith(" "):
        query = query[1:]
    products = Product.objects.all()
    page = request.GET.get('page')
    post_only = request.GET.get('post_only')

    products = products.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query) |
        Q(features__material__icontains=query) |
        Q(features__country_of_origin__icontains=query) |
        Q(images__image_alt__icontains=query) |
        Q(colors__color__icontains=query) |
        Q(unique_id__icontains=query) |
        Q(short_description__icontains=query)
    ).distinct()

    paginator = Paginator(products, 6)  # Show 8 posts per page
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        if post_only:
            return HttpResponse("")
        products = paginator.page(paginator.num_pages)

    context = {
        "products": products,
        "query": query,
    }

    if post_only:
        return render(request, "shop/producs_list.html", context)
    else:
        return render(request, "shop/product_search.html", context)


def category(request,slug):
    form = SortCategoriesForm()
    page = request.GET.get('page')
    sort_by = request.GET.get('sort_by')
    post_only = request.GET.get('post_only')
    categories = Category.objects.all()
    try:
        cat = Category.objects.get(slug=slug)
        products = sort_products(sort_by=sort_by, categories=[cat.id])
        paginator = Paginator(products, 6)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            if post_only:
                return HttpResponse("")
            products = paginator.page(paginator.num_pages)

        context = {
            "categories": categories,
            "products": products,
            "sort_by": sort_by,
            "selected_categories": [cat.id],
            "form": form
        }
        if post_only:
            return render(request, "shop/producs_list.html", context)
        else:
            return render(request, "shop/prducts_with_categories.html", context)
    except Category.DoesNotExist:
        return redirect("shop:shop")






