from django.shortcuts import render
from django.http import HttpResponse



def index_page(request):
    return render(request, "pages/index.html")


def about_us(request):
    return render(request, "pages/about_us.html")


def privacy_policy(request):
    return render(request, "pages/privacy_policy.html")


def frequency_asked_questions(request):
    return render(request, "pages/frequency_asked_questions.html")


def contact(request):
    return render(request, "pages/contact_us.html")


def terms(request):
    return render(request, "pages/terms.html")


def robots(request):
    content = (
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Disallow: /سفارش/\n"
        "Disallow: /حساب-کاربری/\n"
        "Disallow: /کارت/\n"
        "Disallow: /پیام-رسانی/\n"
        "Disallow: /staff/\n"
        "Disallow: /نیکت-پشتیبانی/\n"
        "Allow: /وبلاگ/\n"
        "Allow: /فروشگاه/\n"
        "Allow: /جشنواره-ها/\n"
        "Allow: /\n"
        "Sitemap: https://www.fapo-shop.ir/sitemap.xml\n"
    )
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    response['Content-Encoding'] = 'utf-8'
    return response

