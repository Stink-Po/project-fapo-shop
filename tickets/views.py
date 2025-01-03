from django.shortcuts import  get_object_or_404, redirect
from .models import Tickets, TicketResponse
from .forms import TicketResponseForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from orders.tasks import send_ticket_response_answer


@require_POST
@login_required
def add_comment_to_ticket_profile(request, ticket_id):
    form = TicketResponseForm(request.POST)
    if form.is_valid():
        response = form.cleaned_data["response"]
        ticket = get_object_or_404(Tickets, id=ticket_id)
        new_response = TicketResponse.objects.create(ticket=ticket, user=request.user, response=response)
        if request.user.is_staff:
            ticket.status = Tickets.TicketStatus.APPROVED
            ticket.save()

        new_response.save()
        if request.user.is_staff:
            send_ticket_response_answer.delay(ticket_id=ticket.id, number=ticket.user.phone_number)
            return redirect("staff_area:ticket_details", ticket_id=ticket.id)

        return redirect("accounts:profile_ticket_details", ticket_id=ticket.id)


@login_required
def close_ticket_profile(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)
    ticket.status = Tickets.TicketStatus.CLOSED
    ticket.save()
    if request.user.is_staff:
        return redirect("staff_area:ticket_details", ticket_id=ticket.id)
    return redirect("accounts:profile_ticket_details", ticket_id=ticket.id)
