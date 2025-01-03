from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("ورود-ثبت-نام/", views.login_view, name="login"),
    path("وارد-کردن-رمز-یک-بار-مصرف/", views.input_otp, name="input_otp"),
    path("چک-کردن-رمز-یک-بار-مصرف/", views.verify_otp, name="verify_otp"),
    path("جک-کردن-کاربر/", views.check_user, name="check_user"),
    path("ساخت-کاربر-جدید/", views.create_new_user, name="create_new_user"),
    path("خوش-آمدید/", views.new_user_view, name="welcome"),
    path("خروج/", views.logout_view, name="logout"),
    path("اطلاعات-کاربر/", views.main_profile_view, name="main_profile"),
    path("امتیارات-کاربر/", views.user_profile_score, name="profile_scores"),
    path("ساخن-کد-تخفیف/<int:amount>/", views.create_code, name="generate_discount_code"),
    path("تیکت-پشتیبانی-کاربر/", views.user_profile_tickets, name="user_tickets"),
    path("جزییات-تیکت-پشتیبانی/<int:ticket_id>/", views.profile_ticket_details, name="profile_ticket_details"),
    path("update-user-information/", views.save_profile_information, name="update_profile"),
    path("delete-account/", views.delete_account, name="delete_account"),
    path("orders/", views.profile_orders, name="profile_orders"),
    path("order-details/<int:order_id>/<str:track_id>/", views.user_profile_order_details, name="user_profile_order_details"),
    path("profile/محصولات-مورد-علاقه", views.user_profile_favorites, name="user_profile_favorites"),
    path("profile/لینک-دعوت-دوستان/", views.user_profile_refer_code, name="user_profile_refer_code"),
]