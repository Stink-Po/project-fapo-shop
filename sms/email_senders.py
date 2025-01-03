from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from accounts.models import CustomUser


def send_order_details_function(user, order_id):
    user_name = user.profile.first_name + " " + user.profile.last_name
    title = "اطلاعات خرید"
    body = f"از خرید شما متشکریم {user_name} خرید شما به شماره پیگیری {order_id} دریافت شد و در مرحله پردازش قرار دارد به محض ارسال کد ره گیری مرسوله خدمت شما ارسال میشود  "
    html_message = render_to_string("sms/email_template.html", {"user": user_name, "body": body, "title": title})
    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
        subject="اطلاعات خرید",
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
        body=plain_message,
    )
    message.attach_alternative(html_message, "text/html")

    message.send()


def send_follow_up_code_function(user, order_id, track_code):
    user_name = user.profile.first_name + " " + user.profile.last_name
    title = "کد ره گیری مرسوله"
    body = f"از خرید شما متشکریم {user_name} خرید شما به شماره پیگیری {order_id} به آدرس شما ارسال شد شما میتوانید از طریق آدرس : https://tracking.post.ir/ {track_code} وضعیت مرسوله خود را مشاهده کنید همچنین هرگونه سوال را میتوانید از طریق ارسال تیکت پشتیبانی با کارشناسان ما مطرح نمایید    "
    html_message = render_to_string("sms/email_template.html", {"user": user_name, "body": body, "title": title})
    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
        subject="اطلاعات خرید",
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
        body=plain_message,
    )
    message.attach_alternative(html_message, "text/html")

    message.send()


def send_event_information(event_title, message):
    email_list = []
    users = CustomUser.objects.all()
    for user in users:
        if user.email:
            email_list.append(user.email)

    title = event_title
    subject = "جشنواره خرید فاپو شاپ"
    body_template = message
    html_message = render_to_string("sms/mass_email.html", {"title": title, "body": body_template})
    plain_message = strip_tags(html_message)
    final_message = EmailMultiAlternatives(
        subject=subject,
        from_email=settings.EMAIL_HOST_USER,
        to = [],
        bcc=email_list,
        body=plain_message
    )
    final_message.attach_alternative(html_message, "text/html")
    final_message.send()



