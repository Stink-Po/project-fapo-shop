from . import views
from django.urls import path

app_name = "blog"

urlpatterns = [
    path("", views.blog_main_page, name="main"),
    #re_path(r'(?P<slug>[-\w]+)/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/', views.post_detail, name="post_detail"),

    path("details/<str:slug>/<int:year>/<int:month>/<int:day>/", views.post_detail, name="post_detail"),
    path("submit-comment/<int:post_id>/", views.submit_comment, name="submit_comment"),
    path("search/<str:query>/", views.search_post, name="search"),
    path("categories/<str:slug>/<int:cat_id>/", views.post_by_categories, name="post_by_categories"),

]
