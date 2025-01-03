from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product, ProductColor
from accounts.models import DiscountCodes
from .cart import Cart
from .forms import CartAddProductForm
from django.http import JsonResponse
from orders import tasks
from django.contrib.auth.decorators import login_required
from offers.models import Offer, OfferUsage
import re


@require_POST
def cart_add(request, product_id, color_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    product_color = get_object_or_404(ProductColor, id=color_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            color_id=product_color.id,
            quantity=cd['quantity'],
            override_quantity=cd["override"]
        )
        tasks.add_to_cart.delay(color_id=int(color_id), quantity=int(cd['quantity']))

    return redirect('cart:cart_detail')


@login_required
def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={
                "quantity": item["quantity"],
                "override": True,
            }
        )
    return render(request, "cart/cart_detail.html", )


@require_POST
def product_add_by_json(request):
    cart = Cart(request)
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')
    color_id = request.POST.get('color_id')

    if product_id:
        try:
            product = ProductColor.objects.get(id=color_id).product
            current_product_quantity = ProductColor.objects.get(id=int(color_id)).quantity
            if current_product_quantity >= int(quantity):
                if quantity:
                    cart.add(product, quantity=int(quantity), color_id=int(color_id))
                    tasks.add_to_cart.delay(color_id=int(color_id), quantity=int(quantity))
                else:
                    cart.add(product, quantity=1, color_id=int(color_id))
                    tasks.add_to_cart.delay(color_id=int(color_id), quantity=1)
                return JsonResponse({
                    "status": "ok",
                    "cart_len": len(cart),
                })
            else:
                return JsonResponse({"status": "error", "message": "Product out of stock"})
        except ProductColor.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Product not found"})

    return JsonResponse({"status": "error", "message": "Invalid product ID"})


@require_POST
def update_quantity_by_json(request):
    cart = Cart(request)
    product_id = request.POST.get('product_id')
    color_id = request.POST.get('color_id')
    quantity = int(request.POST.get('quantity'))

    current_quantity = cart.cart.get(f"{product_id}_{color_id}", {}).get('quantity', 0)
    if quantity == 0:
        return JsonResponse({"status": "error", "message": "not availed"})

    try:
        product = Product.objects.get(id=product_id)
        current_product_quantity = ProductColor.objects.get(id=int(color_id)).quantity
        if current_product_quantity == 0:
            if quantity < int(current_quantity):
                tasks.remove_from_cart.delay(color_id=int(color_id))
                cart.add(product, color_id, quantity=quantity, override_quantity=True)
                return JsonResponse({
                    "status": "ok",
                    "cart_len": len(cart),
                })
            else:
                return JsonResponse({"status": "error", "message": "Product out of stock"})
        else:
            if int(current_quantity) > int(quantity):
                tasks.remove_from_cart.delay(color_id=int(color_id))
            elif int(current_quantity) < int(quantity):
                tasks.add_to_cart.delay(color_id=int(color_id))

            cart.add(product, color_id, quantity=quantity, override_quantity=True)
            return JsonResponse({
                "status": "ok",
                "cart_len": len(cart),
            })

    except Product.DoesNotExist or ProductColor.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found"})


@require_POST
def get_cart_by_json(request):
    cart = Cart(request)
    total_discount = 0
    cart_items = []
    for i in cart:
        total_discount += (int(i["price"]) - int(i["discount_price"])) * int(i["quantity"])
        this_product = Product.objects.get(id=i["product_id"])
        cart_items.append(
            {
                "quantity": i["quantity"],
                "price": i["price"],
                "discount": i["discount"],
                "color_id": i["color_id"],
                "product_id": i["product_id"],
                "discount_price": i["discount_price"],
                "product": this_product.name,
                "total_price": i["total_price"],
                "color": i["color_name"],
                "total_discount": (int(i["price"]) - int(i["discount_price"])) * int(i["quantity"]),
                "image_url": Product.objects.get(id=int(i["product_id"])).images.all()[0].image.url

            }
        )
    user = request.user.is_authenticated
    cart_length = len(cart)
    have_discount = cart.have_discount_code
    amount = cart.discount_code_amount
    total_price_of_cart = cart.get_total_price()
    price_of_discount = cart.total_get_price_of_discount

    return JsonResponse(
        {
            "status": "ok",
            "cart": cart_items,
            "cart_length": cart_length,
            "user": user,
            "have_discount": have_discount,
            "amount": amount,
            "price_of_discount": price_of_discount,
            "total_price": total_price_of_cart,
            "total_discount": total_discount,
        }
    )


@require_POST
def cart_remove(request):
    product_id = request.POST.get('product_id')
    color_id = request.POST.get('color_id')

    if product_id != "undefined" and color_id != "undefined":
        if product_id and color_id:
            cart = Cart(request)
            product = get_object_or_404(Product, id=product_id)
            current_quantity = cart.cart.get(f"{product_id}_{color_id}", {}).get('quantity', 0)
            cart.remove(product, color_id=color_id)
            tasks.remove_from_cart.delay(color_id=int(color_id), quantity=current_quantity)

            return JsonResponse({"status": "ok", "message": "Cart is now empty."})

        return JsonResponse({"status": "ok", "message": "Product removed successfully."})

    else:
        return JsonResponse({"status": "error", "message": "Invalid product or color ID"})


@require_POST
def get_cart_len_by_json(request):
    cart = Cart(request)

    return JsonResponse({
        "status": "ok",
        "cart_len": len(cart),
    })


# Helper function to validate discount code format
def is_valid_code_format(code):
    return code and re.match(r'^[A-Za-z0-9]{8,}$', code)


# Helper function to handle offer checks
def validate_offer(user, code):
    email_identifier = user.email if user.email else None
    phone_identifier = user.phone_number if user.phone_number else None

    offer = Offer.objects.filter(code=code).first()
    if offer and offer.check_offer():
        if OfferUsage.objects.filter(user=user, offer=offer,
                                     email_identifier=email_identifier).exists() or OfferUsage.objects.filter(user=user,
                                                                                                              offer=offer,
                                                                                                              phone_identifier=phone_identifier).exists():
            return {"status": "error", "message": "کد وارد شده قبلا توسط شما استفاده شده"}
        return {"status": "ok", "amount": offer.discount_amount}
    return None


# Helper function to handle discount code checks
def validate_discount_code(user, code):
    discount_code = DiscountCodes.objects.filter(user=user, code=code).first()
    if discount_code and discount_code.check_code():
        return {"status": "ok", "amount": discount_code.amount}
    return None


@require_POST
def check_discount_code(request):
    code = request.POST.get('code')
    user = request.user

    # Validate code format
    if not is_valid_code_format(code):

        return JsonResponse({"status": "error", "message": "کد وارد شده صحیح نیست"})

    # Check offer
    offer_result = validate_offer(user, code)
    if offer_result:

        return JsonResponse(offer_result)

    # Check discount code
    discount_code_result = validate_discount_code(user, code)
    if discount_code_result:

        return JsonResponse(discount_code_result)

    # Generic error response
    return JsonResponse({"status": "error", "message": "کد وارد شده صحیح نیست"})


@require_POST
def add_discount_to_cart(request):
    cart = Cart(request)
    code = request.POST.get('code')
    amount = request.POST.get('amount')

    # Validate code format
    if not is_valid_code_format(code):
        return JsonResponse({"status": "error", "message": "کد تخفیف نامعتبر است"})

    # Validate amount
    if not amount or not amount.isdigit():
        return JsonResponse({"status": "error", "message": "مقدار تخفیف نامعتبر است"})

    amount = int(amount)

    # Check and apply offer
    offer = Offer.objects.filter(code=code).first()
    if offer and offer.check_offer() and amount == offer.discount_amount:
        if OfferUsage.objects.filter(user=request.user, offer=offer).exists():
            return JsonResponse({"status": "error", "message": "کد وارد شده قبلا توسط شما استفاده شده"})

        # Apply discount to cart
        request.session["have_discount_code"] = True
        request.session["discount_code"] = code
        cart.have_discount_code = True
        cart.discount_code = code
        cart.discount_code_amount = amount
        cart.save()
        return JsonResponse({"status": "ok"})

    # Check and apply user-specific discount code
    discount_code = DiscountCodes.objects.filter(user=request.user, code=code).first()
    if discount_code and discount_code.check_code() and amount == discount_code.amount:
        # Apply discount to cart
        request.session["have_discount_code"] = True
        request.session["discount_code"] = code
        cart.have_discount_code = True
        cart.discount_code = code
        cart.discount_code_amount = amount
        cart.save()
        return JsonResponse({"status": "ok"})

    # Generic error response
    return JsonResponse({"status": "error", "message": "کد تخفیف معتبر نیست"})
