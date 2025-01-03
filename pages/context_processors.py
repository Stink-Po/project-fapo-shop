from decouple import config
from cart.cart import Cart
from shop.models import Category
from shop.models import Product
from blog.models import Post
from django.db.models import Count
import redis
import random
import string
from django.utils import timezone
from offers.models import Offer
from  urllib.parse import unquote
import os




r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def global_value(request):
    absolute_url = request.build_absolute_uri()
    decoded_url = unquote(absolute_url)
    offers = Offer.objects.filter(is_active=True).filter(image__isnull=False).exclude(image="")
    google_map_api_key = config('GOOGLE_MAP_API')
    user = request.user
    cart = Cart(request)
    categories = Category.objects.all()
    last_blog_posts = Post.published.all()[:7]
    discounted_products = Product.objects.filter(discount__gt=0)[:7]
    timezone.activate('Asia/Tehran')

    discount_dict = {}
    discount_dict_first = {}
    for item in discounted_products:
        discount_dict[item] = generate_random_string()
        discount_dict_first[item] = generate_random_string()

    fav_dict = {}
    favorite_products = Product.objects.annotate(like_count=Count('user_likes')).order_by('-like_count').filter(available=True)[:9]
    for i in favorite_products:
        fav_dict[i] = generate_random_string()
    must_see_dict = {}

    must_see_products = r.zrange("product_ranking", 0, -1, desc=True)
    if must_see_products:
        must_see_products_ids = [int(product_id) for product_id in must_see_products][:7]
        must_see_products = list(Product.objects.filter(id__in=must_see_products_ids).filter(available=True))
        must_see_products.sort(key=lambda x: must_see_products_ids.index(x.id))
        for i in must_see_products:
            must_see_dict[i] = generate_random_string()



    must_sell_dict = {}
    products_must_sell = r.zrange("product_sell", 0, -1, desc=True)
    if products_must_sell:
        product_ids = [int(product_id) for product_id in products_must_sell][:7]
        must_sell_products = list(Product.objects.filter(id__in=product_ids).filter(available=True))
        must_sell_products.sort(key=lambda x: product_ids.index(x.id))
        for item in must_sell_products:
            must_sell_dict[item] = generate_random_string()

    is_staff = request.user.is_staff
    return {
        "user": user,
        "google_map_api_key": google_map_api_key,
        "cart": cart,
        "categories": categories,
        "discounted_products": discount_dict,
        "last_blog_posts": last_blog_posts,
        "favorite_products": fav_dict,
        "must_sell_products": must_sell_dict,
        "must_see_products": must_see_dict,
        "discount_dict_first": discount_dict_first,
        "is_staff": is_staff,
        "offers": offers,
        "canonical": decoded_url,
    }


def change_id_with_product(cart):
    for item in cart:
        # Fetch the product instance using the product_id
        try:
            product = Product.objects.get(id=item['product_id'])
            # Replace 'product_id' with the actual product instance
            item['product'] = product

        except Product.DoesNotExist:
            # Handle the case where the product is not found
            item['product'] = None
    return cart
