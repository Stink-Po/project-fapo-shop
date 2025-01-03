from django.utils import timezone
from django.conf import settings

# Set cart expiration time (in seconds)
CART_EXPIRATION_TIME = 3600  # 1 hour
SEND_WARNING_TIME = 1800

class CartExpirationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the cart exists in the session
        cart = request.session.get(settings.CART_SESSION_ID)
        last_updated_str = request.session.get("last_updated")

        if cart and last_updated_str:
            # Parse last_updated to a timezone-aware datetime
            last_updated = timezone.datetime.fromisoformat(last_updated_str)
            now = timezone.now()
            time_elapsed = (now - last_updated).total_seconds()

            # Check if the cart has expired
            if time_elapsed > CART_EXPIRATION_TIME:
                # Clear the cart and related session data
                request.session.pop(settings.CART_SESSION_ID, None)
                request.session.pop("last_updated", None)
                request.session.pop("have_discount_code", None)
                request.session.pop("discount_code_amount", None)
                request.session.modified = True

        # Continue processing the request
        response = self.get_response(request)
        return response
