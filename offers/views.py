from django.shortcuts import render
from .models import Offer


def offer_list(request):
    future_offers = Offer.get_future_offers()
    active_offers = Offer.get_active_offers()
    out_dated_offers = Offer.get_outdated_offers()

    return render(request, "offers/offers_list.html", {
        "offers": active_offers,
        "future_offers": future_offers,
        "out_dated_offers": out_dated_offers
    })


def offer_detail(request, offer_id):
    try:
        offer = Offer.objects.get(id=offer_id)
    except Offer.DoesNotExist:
        offer = None

    return render(request, 'offers/offer_detail.html', {"offer": offer})

