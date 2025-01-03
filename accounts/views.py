from django.http import Http404
from django.shortcuts import render, redirect, reverse, get_object_or_404
from datetime import datetime, timedelta
from .forms import GetPhoneNumberForm, ProfileForm
from .models import CustomUser, ReferralCode, Profile, DiscountCodes, UserIdentifier
from django.contrib.auth import login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from tickets.models import Tickets, TicketResponse
from tickets.forms import TicketsForm, TicketResponseForm
from django.core.exceptions import PermissionDenied
from orders.models import Order
from shop.models import Product
from  urllib.parse import unquote


def paginate_results(request, queryset, num_items=5):
    paginator = Paginator(queryset, num_items)
    page_number = request.GET.get("page", 1)

    try:
        results = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        results = paginator.page(1)
    return results


def paginate_results_list(request, queryset, num_items=8):
    paginator = Paginator(queryset, num_items)
    page_number = request.GET.get("page", 1)

    try:
        results = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        results = paginator.page(1)
    return results


@login_required
def logout_view(request):
    logout(request)
    return redirect("pages:index")


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        logout(request)
        return redirect("pages:index")

    return render(request, "accounts/profile/base_profile.html",
                  {
                      "section": "delete",
                  }
                  )


def login_view(request):
    form = GetPhoneNumberForm()
    if request.user.is_authenticated:
        return redirect("pages:index")
    referral_code = request.GET.get('ref', None)
    if referral_code:
        request.session["referral_code"] = referral_code
    if request.method == 'POST':
        form = GetPhoneNumberForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone']
            request.session["phone"] = phone_number
            return redirect("sms:send_otp")

    return render(request, 'accounts/login.html', {'form': form})


def input_otp(request):
    if request.user.is_authenticated:
        return redirect("pages:index")
    return render(request, "accounts/input_otp.html")


@require_POST
def verify_otp(request):
    data = json.loads(request.body)
    user_otp = data.get('otp')
    site_otp = request.session.get("otp")
    otp = site_otp.get("otp")
    timestamp = datetime.fromisoformat(site_otp.get("timestamp"))
    redirect_url = reverse('accounts:check_user')
    if timestamp + timedelta(minutes=3) < datetime.now():
        return JsonResponse({'success': False, "message": "زمان استفاده از کد یک بار مصرف سپری شده"})
    elif int(user_otp) != int(otp):
        return JsonResponse({'success': False, "message": "کد وارد شده اشتباه است"})
    elif int(user_otp) == int(otp) and timestamp + timedelta(minutes=3) > datetime.now():
        del request.session["otp"]
        return JsonResponse({'success': True, 'redirect_url': redirect_url})



def check_user(request):
    user_phone = request.session["phone"]
    try:
        user = CustomUser.objects.get(phone_number=user_phone)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return redirect("pages:index")
    except CustomUser.DoesNotExist:
        return redirect("accounts:create_new_user")


def create_new_user(request):
    new_user = CustomUser.objects.create_user(phone_number=request.session["phone"])
    unique_identifier = new_user.phone_number if new_user.phone_number else new_user.email
    user_exists_before = UserIdentifier.objects.filter(identifier=unique_identifier).exists()
    if not user_exists_before:
        UserIdentifier.objects.create(identifier=unique_identifier)
    
    new_user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, new_user)
    new_user.is_new = False
    new_user.save()
    if user_exists_before:
        return redirect("accounts:main_profile")
    return redirect("accounts:welcome")


@login_required
def new_user_view(request):
    form = ProfileForm()
    return render(request, "accounts/new_user_view.html", {"form": form})


# User profile views

@login_required
def main_profile_view(request):
    form = ProfileForm()
    return render(request, "accounts/profile/base_profile.html", {
        "section": "main",
        "form": form,
    })


@require_POST
@login_required
def save_profile_information(request):
    form = ProfileForm(request.POST, user=request.user)
    if form.is_valid():
        current_user = CustomUser.objects.get(id=request.user.id)
        current_user_profile = Profile.objects.get(user=request.user)
        current_user.phone_number = form.cleaned_data['phone']
        current_user.email = form.cleaned_data['email']
        current_user.first_name = form.cleaned_data['first_name']
        current_user.last_name = form.cleaned_data['last_name']
        current_user.save()
        current_user_profile.zip_code = form.cleaned_data['zip_code']
        current_user_profile.province = str(form.cleaned_data['province'])
        current_user_profile.city = str(form.cleaned_data['city'])
        current_user_profile.address = form.cleaned_data['address']
        current_user_profile.first_name = form.cleaned_data['first_name']
        current_user_profile.last_name = form.cleaned_data['last_name']
        current_user_profile.email = form.cleaned_data['email']
        current_user_profile.save()
        return redirect("accounts:main_profile")

    else:

        return render(request, "accounts/profile/base_profile.html", {
            "section": "main",
            "form": form,
            "form_has_errors": True,
        })


@login_required
def user_profile_score(request):
    range_list = [i * 10 for i in range(1, 7)]
    user_discount_codes = DiscountCodes.objects.filter(user=request.user).order_by("-created")
    user_discount_codes = paginate_results(request, user_discount_codes)
    return render(request, "accounts/profile/base_profile.html",
                  {
                      "range_list": range_list,
                      "user_discount_codes": user_discount_codes,
                      "section": "score",
                  }
                  )


@login_required
def create_code(request, amount: int):
    if request.user.score >= amount * 100:
        this_user = CustomUser.objects.get(id=request.user.id)
        DiscountCodes.objects.create(user=this_user, amount=amount * 10)
        this_user.decrease_score(score=amount * 100)
    else:
        raise PermissionDenied
    return redirect("accounts:profile_scores")


# User profile Tickets
@login_required
def user_profile_tickets(request):
    form = TicketsForm()
    if request.method == "POST":
        form = TicketsForm(request.POST)
        if form.is_valid():
            new_ticket = Tickets.objects.create(
                user=request.user,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
            )
            new_ticket.save()
            response = "سلام دوست عزیز\nتیکت شما در صف کار یکی از همکاران ما قرار گرفت.\nبه زودی شما را تا حل مشکل همراهی میکنیم."
            response = response.replace("\n", "<br>")
            new_response = TicketResponse.objects.create(ticket=new_ticket, user=CustomUser.objects.get(id=1), response=response)
            new_response.save()
            new_ticket.save()

    user_tickets = Tickets.objects.filter(user=request.user).order_by("-created")
    user_tickets = paginate_results_list(request, user_tickets)
    return render(request, "accounts/profile/base_profile.html",
                  {"section": "tickets",
                   "user_tickets": user_tickets,
                   "form": form,
                   }
                  )


@login_required
def profile_ticket_details(request, ticket_id):
    form = TicketResponseForm()
    try:
        ticket = get_object_or_404(Tickets, user=request.user, id=ticket_id)
        try:
            responses = TicketResponse.objects.filter(ticket=ticket)
        except TicketResponse.DoesNotExist:
            responses = None
        return render(request, "accounts/profile/base_profile.html",
                      {
                          "section": "ticket_info",
                          "form": form,
                          "ticket": ticket,
                          "responses": responses,
                      }
                      )
    except Tickets.DoesNotExist:
        pass

        return render(request, "accounts/profile/base_profile.html",
                      {
                          "section": "ticket_info",
                          "form": form,

                      }
                      )


@login_required
def profile_orders(request):
    user_orders = Order.objects.filter(user=request.user).exclude(track_id__isnull=True).exclude(track_id="")
    user_orders = paginate_results_list(request, user_orders)
    context = {
        "section": "orders_list",
        "orders": user_orders,
    }
    return render(request, "accounts/profile/base_profile.html", context)


@login_required
def user_profile_order_details(request, order_id, track_id):
    order = Order.objects.filter(id=order_id, track_id=track_id).first()
    if order:
        return render(request, "accounts/profile/base_profile.html", {"section": "order_detail", "order": order})
    else:
        raise Http404


@login_required
def user_profile_favorites(request):
    user_favorite_products = Product.objects.filter(user_likes=request.user)
    user_favorite_products = paginate_results_list(request, user_favorite_products)
    context = {
        "section": "favorite_products",
        "favorite_products": user_favorite_products,
    }
    return render(request, "accounts/profile/base_profile.html", context)


@login_required
def user_profile_refer_code(request):
    user_invites = ReferralCode.objects.get(user=request.user).invites
    refer_code = ReferralCode.objects.get(user=request.user).code
    singing_url = reverse("accounts:login")
    refer_url = unquote(request.build_absolute_uri(f"{singing_url}?ref={refer_code}"))

    context = {
        "section": "refer",
        "refer_url": refer_url,
        "user_invites": user_invites,
    }
    return render(request, "accounts/profile/base_profile.html", context)
