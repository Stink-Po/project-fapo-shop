from django.shortcuts import render
from tickets.models import Tickets
from orders.models import Order, Payment
from offers.models import Offer
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from shop.models import ProductsProfit
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from offers.forms import OfferForm
from tickets.forms import TicketResponseForm
from orders.tasks import send_follow_up_code, send_offers
from blog.persian_date_convert import convert_date_persian_numbers


def ret_profit():
    try:
        profit = ProductsProfit.objects.get(id=1)
    except ProductsProfit.DoesNotExist:
        profit = None
    return profit


def paginate_results_list(request, queryset, num_items=20):
    paginator = Paginator(queryset, num_items)
    page_number = request.GET.get("page", 1)

    try:
        results = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        results = paginator.page(1)
    return results


@staff_member_required
@require_POST
def get_new_data(request):
    len_active_offers = Offer.objects.filter(is_active=True).count()
    len_new_orders = Order.objects.filter(status=Order.OrderChoices.PROCESSIONING).count()
    len_active_tickets = Tickets.objects.exclude(status=Tickets.TicketStatus.CLOSED).count()
    return JsonResponse({
        "status": "ok",
        "active_offers": len_active_offers,
        "active_tickets": len_active_tickets,
        "active_orders": len_new_orders
    })


@staff_member_required
def main_admin_view(request):
    profit = ret_profit()
    tickets = Tickets.objects.exclude(status=Tickets.TicketStatus.CLOSED)[:5]
    orders = Order.objects.filter(status=Order.OrderChoices.PROCESSIONING).order_by("-updated")[:5]
    offers = Offer.objects.filter(is_active=True)[:5]

    return render(request, "staff_area/main_staff.html", {
        "section": "main",
        "profit": profit,
        "tickets": tickets,
        "offers": offers,
        "orders": orders,
    }
                  )


@staff_member_required
def main_orders_admin_view(request):
    orders = Order.objects.all()
    orders = paginate_results_list(request, queryset=orders)
    profit = ret_profit()
    return render(request, "staff_area/main_staff.html", {
        "section": "orders",
        "orders": orders,
        "profit": profit,
    })


@staff_member_required
def main_tickets_admin_view(request):
    tickets = Tickets.objects.exclude(status=Tickets.TicketStatus.CLOSED).order_by("-updated")
    tickets = paginate_results_list(request, queryset=tickets)
    profit = ret_profit()

    return render(request, "staff_area/main_staff.html",
                  {"section": "tickets", "tickets": tickets, "profit": profit}
                  )


@staff_member_required
def main_offers_admin_view(request):
    profit = ret_profit()
    offers = Offer.objects.all()
    offers = paginate_results_list(request=request, queryset=offers)
    form = OfferForm()
    if request.method == 'POST':
        form = OfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer_instance = form.save()
            offer_start_date = form.cleaned_data['start_date'].date()
            offer_end_date = form.cleaned_data['end_date'].date()
            offer_start_date = convert_date_persian_numbers(offer_start_date)
            offer_end_date = convert_date_persian_numbers(offer_end_date)
            message = (
                f"سلام در جشنواره {offer_instance.name} "
                f"از تاریخ {offer_start_date} تا {offer_end_date} "
                f"با وارد کردن کد {offer_instance.code} "
                f"در سبد خرید به میزان {offer_instance.discount_amount} درصد تخفیف دریافت کنید. "
                f"منتظر شما در فاپو شاپ هستیم. "
                f"https://fapo-shop.ir"
            )
            if offer_instance.image and offer_instance.image != "":
                send_offers.delay(message= message, title=offer_instance.name)
    return render(request, "staff_area/main_staff.html",
                  {
                      "section": "events",
                      "form": form,
                      "offers": offers,
                      "profit": profit,
                  }
                  )


@staff_member_required
def ticket_details_admin_view(request, ticket_id):
    profit = ret_profit()
    form = TicketResponseForm()
    try:
        ticket = Tickets.objects.get(id=ticket_id)
    except Tickets.DoesNotExist:
        ticket = None

    return render(request, "staff_area/main_staff.html",
                  {"section": "ticket", "form": form, "ticket": ticket, "profit": profit, })


@staff_member_required
def order_details_admin_view(request, order_id):
    profit = ret_profit()
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        order = None
    if order:
        payment = Payment.objects.get(order=order)
        if request.method == "POST":
            follow_up_code = request.POST["follow_up_code"]
            if follow_up_code:
                order.post_follow_up = follow_up_code
                order.status = Order.OrderChoices.SEND
                order.save()
                send_follow_up_code.delay(order_id=f"{order.id}/{order.track_id}", user_id=order.user.id,
                                          track_code=follow_up_code)
    else:
        payment = None
    return render(request, "staff_area/main_staff.html",
                  {"order": order, "section": "order", "profit": profit, "payment": payment})


@staff_member_required
def print_address(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        order = None
    if order:
        return render(request, 'staff_area/print_address.html', {"order": order})
