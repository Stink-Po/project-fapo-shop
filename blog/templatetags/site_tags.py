from datetime import timedelta, datetime
from django import template
from blog.persian_date_convert import convert_date
from shop.models import Product

register = template.Library()

@register.filter
def convert_to_persian_date(value):
    persian_date = convert_date(value)
    return persian_date





@register.filter
def compare_score(user_score, value):
    if user_score >= value * 100:
        return True
    return False


persian_digits = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
}

def convert_to_persian_numbers(value):
    # Convert English digits to Persian digits
    return ''.join(persian_digits.get(char, char) for char in value)

@register.filter
def time_to_persian(value):
    return value.strftime('%H:%M') if value else ''


@register.filter(name='compare_dates')
def compare_dates(date1, date2):
    if date1.replace(microsecond=0) == date2.replace(microsecond=0):
        return False
    return True

@register.simple_tag
def get_product(product_id):
    try:
        return Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return None


@register.filter
def multiply(value, arg):
    try:
        return int(float(value) * float(arg)) * 10
    except (ValueError, TypeError):
        return 0


@register.filter
def date_convertor(value):
    """Converts a datetime object to 'YYYY-MM-DD' format."""
    return value.strftime('%Y-%m-%d') if value else ''


@register.filter
def time_convertor(value):
    today = datetime.today()
    value = datetime.combine(today, value) + timedelta(hours=3, minutes=30)
    """Converts a datetime object to 'HH:MM' format."""
    return value.strftime('%H:%M') if value else ''


@register.filter
def division(value):
    try:
        return int(value * 5)
    except ZeroDivisionError:
        return int(0)