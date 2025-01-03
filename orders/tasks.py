import random
from celery import shared_task
from orders.models import Order
from shop.models import Product, ProductColor, ProductsProfit
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.contrib.sessions.models import Session
from sms.sms_senders import send_cart_warning, successful_payment, send_ticket_response, send_post_code, event_sender
from accounts.models import CustomUser
from sms.email_senders import send_order_details_function, send_follow_up_code_function, send_event_information
from offers.models import Offer
import subprocess
from django.core.mail import EmailMessage
import os
from datetime import datetime
import shlex


@shared_task
def add_to_cart(color_id, quantity: int = 1):
    """
    Task to Remove quanitity from a product if adding to shopping cart.
    """

    try:
        this_product = ProductColor.objects.get(id=color_id)
        if this_product.quantity != 0 or this_product.reserved_quantity != 0:
            this_product.quantity -= quantity
            this_product.reserved_quantity += quantity
            this_product.save()
            check_for_available_products()

    except ProductColor.DoesNotExist or Exception:
        return


@shared_task
def remove_from_cart(color_id, quantity: int = 1):
    """
        Task to add quanitity from a product if they remove from shopping cart.
        """

    try:
        this_product = ProductColor.objects.get(id=color_id)

        if this_product.reserved_quantity - quantity >= 0:
            this_product.quantity += quantity
            this_product.reserved_quantity -= quantity
            this_product.save()
            check_for_available_products()

    except ProductColor.DoesNotExist or Exception:
        return


@shared_task
def check_for_available_products():
    products = Product.objects.all()
    # Loop through each product
    for product in products:
        # Get the total quantity of all colors for this product
        total_quantity = sum(color.quantity for color in product.colors.all())

        # If total quantity is 0, mark the product as unavailable
        if total_quantity == 0:
            if product.available:
                product.available = False
                product.save()


        # If there is any stock, mark the product as available
        else:
            if not product.available:
                product.available = True
                product.save()


CART_EXPIRATION_TIME = timedelta(minutes=60)
SEND_WARNING_TIME = timedelta(minutes=30)


@shared_task
def clear_abandoned_carts():
    expired_time = timezone.now() - CART_EXPIRATION_TIME
    warning_time = timezone.now() - SEND_WARNING_TIME

    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        data = session.get_decoded()
        last_updated_str = data.get("last_updated")
        cart = data.get(settings.CART_SESSION_ID)

        if cart and last_updated_str and len(cart) != 0:
            last_updated = timezone.datetime.fromisoformat(last_updated_str)

            if last_updated < expired_time:
                # Clear cart if expired
                for key, item in cart.items():
                    color_id = item["color_id"]
                    quantity = item["quantity"]
                    try:
                        remove_from_cart(color_id, int(quantity))
                    except ProductColor.DoesNotExist:
                        pass  # Handle as needed

                # Clear session data
                session_data = session.get_decoded()
                session_data.pop(settings.CART_SESSION_ID, None)
                session_data.pop("last_updated", None)
                session_data.pop("have_discount_code", None)
                session_data.pop("discount_code_amount", None)
                session_data.pop("sms_sent", None)
                session_data["modified"] = True
                session.session_data = Session.objects.encode(session_data)
                session.save()

            elif last_updated < warning_time:
                # Check if the SMS warning was already sent
                if not data.get("sms_sent"):  # Proceed only if SMS hasn't been sent
                    user_id = data.get("user_id")
                    if user_id:
                        try:
                            user = CustomUser.objects.get(id=user_id)
                            if user.phone_number:
                                phone_number = user.phone_number
                                send_cart_warning(int(phone_number))  # Send SMS

                                # Mark SMS as sent in session data
                                session_data = session.get_decoded()
                                session_data["sms_sent"] = True
                                session_data["modified"] = True
                                session.session_data = Session.objects.encode(session_data)
                                session.save()

                                # Debug: Confirm `sms_sent` flag after save
                                updated_data = session.get_decoded()  # Re-fetch session data


                        except CustomUser.DoesNotExist:
                            pass


@shared_task
def send_card_warning_sms(phone_number):
    """
    send sms to user about shopinhg card

    """
    send_cart_warning(number=phone_number)


@shared_task
def complete_order_products(order_id):
    try:
        order = Order.objects.get(id=order_id)
        for item in order.items.all():
            color_id = item.color_obj.id
            this_product = ProductColor.objects.get(id=color_id)
            this_product.reserved_quantity -= item.quantity
            this_product.save()

    except Order.DoesNotExist:
        return


@shared_task
def fail_payment_reverse_products(order_id):
    try:
        order = Order.objects.get(id=order_id)
        for item in order.items.all():
            color_id = item.color_obj.id
            this_product = ProductColor.objects.get(id=color_id)
            this_product.reserved_quantity -= item.quantity
            this_product.quantity += 1
            this_product.save()

    except Order.DoesNotExist:
        return


@shared_task
def send_order_details(order_id, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        if user.email or user.profile.email:
            send_order_details_function(user=user, order_id=order_id)
        if user.phone_number or user.profile.phone_number:
            number = user.phone_number if user.phone_number else user.profile.phone_number
            successful_payment(number=number, order_id=order_id)
    except CustomUser.DoesNotExist:
        return


@shared_task
def send_follow_up_code(order_id, user_id, track_code):
    try:
        user = CustomUser.objects.get(id=user_id)
        if user.email or user.profile.email:
            send_follow_up_code_function(user=user, order_id=order_id, track_code=track_code)
        if user.phone_number or user.profile.phone_number:
            number = user.phone_number if user.phone_number else user.profile.phone_number
            send_post_code(number, track_code)

    except CustomUser.DoesNotExist:
        return


@shared_task
def site_income(order_id):
    try:
        order = Order.objects.get(id=order_id)
        # Unpack the result of get_or_create
        income_record, created = ProductsProfit.objects.get_or_create(id=1)
        total = 0

        for item in order.items.all():
            if order.discount_amount != 0:
                total += (item.product.get_profit(cart_discount=order.discount_amount) * item.quantity)
            else:
                total += (item.product.get_profit() * item.quantity)

        # Update the profit and sell_prices
        income_record.profit += total
        income_record.sell_prices += order.get_total_cost()
        income_record.save()

    except Order.DoesNotExist:
        return


OFFER_TIME = timedelta(days=1)


@shared_task
def product_discount():
    check_for_available_products()
    all_products = Product.objects.all()
    for item in all_products:
        item.discount = 0
        item.offer_end = None
        item.save()
    available_products = Product.objects.filter(available=True)
    random_products = []
    for i in range(5):
        random_products.append(random.choice(available_products))

    discount_range = [3, 5, 10]
    for product in random_products:
        discount = random.choice(discount_range)
        product.discount = discount
        tehran_time = timezone.now() + timedelta(hours=3, minutes=30)
        product.offer_end = tehran_time + OFFER_TIME
        product.save()


@shared_task
def check_offers():
    offers = Offer.objects.exclude(is_active=False)
    if offers and offers != []:
        this_time = timezone.now()
        for offer in offers:
            if offer.end_date <= this_time:
                offer.is_active = False
                offer.save()
    else:
        return


@shared_task
def send_ticket_response_answer(number, ticket_id):
    if number and ticket_id:
        send_ticket_response(number, ticket_id)
    else:
        return


@shared_task
def send_offers(message, title):
    users_phone_numbers = []
    send_event_information(message=message, event_title=title)
    users = CustomUser.objects.all()
    for user in users:
        if user.phone_number:
            users_phone_numbers.append(user.phone_number)

    event_sender(number=users_phone_numbers, message=message)


@shared_task
def backup_database():
    # Define the backup file name and path
    backup_filename = f"db_backup_{datetime.now().strftime('%Y-%m-%d')}.sql"
    backup_file_path = os.path.join(os.path.dirname(__file__), 'backups', backup_filename)

    # Command to run pg_dump
    command = [
        "pg_dump",
        "-h", "postgres_db",  # Hostname of the PostgreSQL container
        "-U", settings.DATABASES['default']['USER'],
        "-d", settings.DATABASES['default']['NAME'],
        "-f", backup_file_path
    ]

    try:
        # Set the environment variable for the PostgreSQL password
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.DATABASES['default']['PASSWORD']

        # Run the pg_dump command
        subprocess.run(command, env=env, check=True)

        # Prepare the email with the backup file as an attachment
        email = EmailMessage(
            subject=f"Database Backup: {datetime.now().strftime('%Y-%m-%d')}",
            body="Please find the database backup attached.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["email@email.com"]
        )

        # Attach the backup file
        with open(backup_file_path, 'rb') as backup_file:
            email.attach(backup_filename, backup_file.read(), 'application/sql')

        # Send the email
        email.send(fail_silently=False)

        # Optionally, remove the backup file after sending it
        os.remove(backup_file_path)

    except Exception as e:
        # Log the error or send an alert if the task fails
        print(f"Error during database backup: {e}")
