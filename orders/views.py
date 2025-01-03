from django.templatetags.static import static
from django.http import HttpResponse, Http404, HttpResponseNotAllowed
from django.template.loader import render_to_string
import weasyprint
import requests
from .forms import OrderAdressForm
from django.contrib.auth.decorators import login_required
from accounts.models import Profile, CustomUser
from . import tasks
from .models import Order, OrderItem, Payment
from shop.models import Product, ProductColor
from cart.cart import Cart
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from datetime import datetime
import os
from accounts.models import DiscountCodes
import redis
from offers.models import Offer, OfferUsage
from decouple import config
from django.conf import settings




r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))

@login_required
def get_order_address(request):
    form = OrderAdressForm()

    return render(request, "orders/enter_order_address.html", {'form': form})


@login_required
def get_new_order_address(request):
    cart = Cart(request)
    if len(cart) != 0:
        pass
        if cart.have_discount_code:
            discount_amount = cart.discount_code_amount
            discount_code = cart.discount_code
        else:
            discount_code = ""
            discount_amount = 0
        if request.method == "POST":
            form = OrderAdressForm(request.POST)
            if form.is_valid():
                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]
                phone = form.cleaned_data["phone"]
                address = form.cleaned_data["address"]
                zip_code = form.cleaned_data["zip_code"]
                city = str(form.cleaned_data["city"])
                province = str(form.cleaned_data["province"])
                email = form.cleaned_data["email"]

                if not request.user.profile.address:

                    user_profile, created = Profile.objects.get_or_create(user=request.user)
                    user_profile.first_name = first_name
                    user_profile.last_name = last_name
                    user_profile.email = email
                    user_profile.province = province
                    user_profile.city = city
                    user_profile.zip_code = zip_code
                    user_profile.address = address
                    user_profile.save()
                    if not request.user.phone_number:
                        this_user = CustomUser.objects.get(id=request.user.id)
                        this_user.phone_number = phone
                        this_user.save()
                new_order = save_order(user=request.user,
                                       address=address,
                                       zip_code=zip_code,
                                       city=city,
                                       province=province,
                                       email=email,
                                       first_name=first_name,
                                       last_name=last_name,
                                       discount_code=discount_code,
                                       amount=discount_amount,
                                       phone=phone)
                save_order_items(order=new_order, cart=cart)
                set_order_id(request, new_order.id)

                return render(request, "orders/order_with_new_address.html", {
                    "order": new_order
                })


        else:
            form = OrderAdressForm()

        return render(request, "orders/enter_order_address.html", {'form': form})
    else:
        return HttpResponseNotAllowed


@login_required
def save_order_with_user_profile_information(request):
    cart = Cart(request)
    if len(cart) != 0:
        if cart.have_discount_code:
            discount_amount = cart.discount_code_amount
            discount_code = cart.discount_code
        else:
            discount_code = ""
            discount_amount = 0

        this_user = CustomUser.objects.get(id=request.user.id)
        new_order = save_order(
            user=this_user,
            address=this_user.profile.address,
            zip_code=this_user.profile.zip_code,
            city=this_user.profile.city,
            email=this_user.profile.email,
            first_name=this_user.profile.first_name,
            last_name=this_user.profile.last_name,
            discount_code=discount_code,
            amount=discount_amount,
            phone=this_user.phone_number,
            province=this_user.profile.province,

        )
        order_id = new_order.id
        set_order_id(request, order_id)

        save_order_items(order=new_order, cart=cart)

        return redirect("orders:send_request")
    else:
        return HttpResponseNotAllowed


# payments views
@login_required
def send_request(request):
    cart = Cart(request)
    if cart.have_discount_code:
        discount_code = cart.discount_code
        offer = Offer.objects.filter(code=discount_code).first()
        if offer and offer.check_offer():

            user = request.user
            email_identifier = user.email if user.email else None
            phone_identifier = user.phone_number if user.phone_number else None

            if OfferUsage.objects.filter(user=user, offer=offer,
                                         email_identifier=email_identifier).exists() or OfferUsage.objects.filter(
                user=user,
                offer=offer,
                phone_identifier=phone_identifier).exists():
                cart.discount_code = None
                cart.have_discount_code = False
                cart.discount_code_amount = 0
                cart.total_discount = None
                cart.save()
            else:

                OfferUsage.objects.create(user=request.user, offer=offer, email_identifier=email_identifier,
                                          phone_identifier=phone_identifier)


        else:
            try:
                this_discount_code = DiscountCodes.objects.get(code=discount_code)
                this_discount_code.used = True
                this_discount_code.save()
            except DiscountCodes.DoesNotExist:
                cart.discount_code = None
                cart.have_discount_code = False
                cart.discount_code_amount = 0
                cart.total_discount = None
                cart.save()

    amount = (cart.get_total_price() + 70000) * 10
    order_id = request.session.get('order_id')
    amount = int(amount)
    data = {
        "amount": amount,
        "merchant": config("ZIBAL_MERCHANT"),  # set this in .env
        "callbackUrl": "https://fapo-shop.ir/order/callback",
        "orderId": order_id,
        "mobile": f"{request.user.phone_number}",

    }
    try:
        response = requests.post(url="https://gateway.zibal.ir/v1/request", json=data)
    except TimeoutError:
        return JsonResponse({"data": "fail"})
    result = response.json()

    if result["result"] == 100:
        try:
            this_order = Order.objects.get(id=order_id)
            this_order.track_id = result['trackId']
            this_order.save()
        except Order.DoesNotExist:
            return Http404
        link = f"https://gateway.zibal.ir/start/{result['trackId']}"
        cart.clear()
        return render(request, "orders/redirect_to_bank.html", {"link": link})
    return JsonResponse(result)


def call_back(request):
    success = request.GET.get("success")
    order_id = request.GET.get("orderId")
    follow_up_number = request.GET.get("trackId")
    status = request.GET.get("status")

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        order = None

    user = Order.objects.filter(id=order_id, track_id=follow_up_number).first().user

    if user:
        try:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
        except Exception:
            return Http404
    payment = Payment.objects.create(
        user=user,
        order=order,
        track_id=follow_up_number,
    )
    payment.status = status
    payment.save()
    if int(success) == 1:
        data = {
            "trackId": follow_up_number,
            "merchant": config("ZIBAL_MERCHANT"),
        }
        verify_method = requests.post(url="https://gateway.zibal.ir/v1/verify", json=data)
        verify_result = verify_method.json()
        payment.timestamp = datetime.fromisoformat(verify_result.get('paidAt')) if verify_result.get('paidAt') else None
        payment.card_number = verify_result['cardNumber'] if verify_result.get("cardNumber") else None
        payment.status = verify_result['status'] if verify_result.get("status") else None
        payment.amount = verify_result['amount'] if verify_result.get("amount") else None
        payment.ref_number = verify_result['refNumber'] if verify_result.get("refNumber") else None
        payment.description = verify_result['description'] if verify_result.get("description") else None
        payment.result = verify_result['result'] if verify_result.get("result") else None
        payment.message = verify_result['message'] if verify_result.get("message") else None
        payment.save()

        if verify_result.get("status"):
            if verify_result['status'] == 1:
                if order:
                    tasks.site_income.delay(order_id=order.id)
                    order.paid = True
                    order.save()
                    user = CustomUser.objects.get(id=request.user.id)
                    user.add_score(score=10)
                    user.save()
                tasks.complete_order_products.delay(order_id=order_id)
                tasks.send_order_details.delay(user_id=request.user.id, order_id=f"{order_id}/{order.track_id}")
                return render(request, "orders/success-payment.html", {"data": payment, "track_id": follow_up_number})

        else:
            if order:
                order.status = Order.OrderChoices.FAIL
                order.save()
            tasks.fail_payment_reverse_products.delay(order_id=order_id)
            if verify_result.get("status"):
                error_status = get_payment_status(verify_result['status'])
            else:
                error_status = ""
            return render(request, "orders/fail-payment.html", {
                "data": follow_up_number, "order_id": order_id, "order": order, "error_status": error_status
            })

    else:
        if order:
            order.status = Order.OrderChoices.FAIL
            order.save()
        tasks.fail_payment_reverse_products.delay(order_id=order_id)
        return render(request, "orders/fail-payment.html",
                      {"data": follow_up_number, "order_id": order_id, "order": order})


@login_required
def factor(request, order_id, track_id):
    order = Order.objects.filter(id=order_id, track_id=track_id).first()
    if order:
        return render(request, "orders/factor.html", {"order": order, "download": False})

    return Http404


@login_required
def download_factor(request, order_id, track_id):
    order = Order.objects.filter(id=order_id, track_id=track_id).first()
    logo_path = request.build_absolute_uri(static('assets/image/logo.png'))
    if settings.DEBUG:
        css_path = os.path.join(settings.STATICFILES_DIRS[0], 'assets', 'css', 'bootstrap.rtl.min.css')
    else:
        css_path = os.path.join(settings.STATIC_ROOT, 'assets', 'css', 'bootstrap.rtl.min.css')
    print(f"logo path : {logo_path}")
    print(f"css path : {css_path}")
    html = render_to_string('orders/factor.html',
                            {'order': order, 'logo': logo_path, "download": True})
    css = weasyprint.CSS(filename=css_path)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=[css])
    return response
    # end of payment views


def save_order(user, first_name, last_name, phone, address, zip_code, city, province, email, amount,
               discount_code=None, ):
    new_order = Order.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        postal_code=zip_code,
        city=city,
        province=province,
        address=address,
        email=email,
        discount_amount=amount,
        discount_code=discount_code if discount_code else ""
    )
    return new_order


def save_order_items(cart, order):
    for item in cart:
        product = Product.objects.get(id=item["product_id"])
        r.zincrby("product_sell", 1, product.id)
        price = item["price"]
        quantity = item["quantity"]
        color = ProductColor.objects.get(id=item["color_id"]).get_color_display()
        discount = item["discount"]
        OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity, color=color,
                                 discount=discount, color_obj=ProductColor.objects.get(id=item["color_id"]))


def set_order_id(request, order_id):
    try:
        if request.session['order_id']:
            del request.session['order_id']
        request.session['order_id'] = order_id
        request.session.modified = True
    except KeyError:
        request.session['order_id'] = order_id
        request.session.modified = True
        return


def get_payment_status(status: int):
    status_messages = {
        -1: "در انتظار پردخت",
        -2: "خطای داخلی",
        1: "پرداخت شده - تاییدشده",
        2: "پرداخت شده - تاییدنشده",
        3: "لغوشده توسط کاربر",
        4: "‌شماره کارت نامعتبر می‌باشد.",
        5: "‌موجودی حساب کافی نمی‌باشد.",
        6: "رمز واردشده اشتباه می‌باشد.",
        7: "‌تعداد درخواست‌ها بیش از حد مجاز می‌باشد.",
        8: "‌تعداد پرداخت اینترنتی روزانه بیش از حد مجاز می‌باشد.",
        9: "مبلغ پرداخت اینترنتی روزانه بیش از حد مجاز می‌باشد.",
        10: "‌صادرکننده‌ی کارت نامعتبر می‌باشد.",
        11: "‌خطای سوییچ",
        12: "کارت قابل دسترسی نمی‌باشد.",
        15: "تراکنش استرداد شده",
        16: "تراکنش در حال استرداد",
    }
    return status_messages[status]
