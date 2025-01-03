from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from .models import PostCategory, Post, PostComment
import redis
from .forms import SearchForm, CommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.contrib.postgres.search import SearchVector
from shop.models import Product
from random import sample
import os
from django.conf import settings




r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))




def blog_main_page(request):
    page = request.GET.get('page', 1)
    try:
        int(page)
    except ValueError or TypeError:
        page = 1

    post_only = request.GET.get('post_only')
    post_ranking = r.zrange("post_ranking", 0, -1)
    post_ranking_ids = [int(post_id) for post_id in post_ranking]
    most_viewed_post = list(Post.objects.filter(id__in=post_ranking_ids))
    most_viewed_post.sort(key=lambda x: post_ranking_ids.index(x.id))
    form = SearchForm()
    all_categories = PostCategory.objects.all()
    post_list = Post.published.all()
    paginator = Paginator(post_list, 8)  # Show 8 posts per page

    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        if post_only:
            return HttpResponse("")
        post_list = paginator.page(paginator.num_pages)

    context = {
        "form": form,
        "all_categories": all_categories,
        "post_list": post_list,
        "most_viewed_post": most_viewed_post,
    }

    if post_only:
        return render(request, "blog/post_list.html", context)
    else:
        return render(request, "blog/blog.html", context)


def post_detail(request, year, month, day, slug):
    form = SearchForm()
    comment_form = CommentForm()
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             slug=slug, publish__year=year,
                             publish__month=month, publish__day=day)
    try:
        post_comments = PostComment.objects.filter(post=post, parent=None)
    except PostComment.DoesNotExist:
        post_comments = None

    r.zincrby("post_ranking", 1, post.id)
    must_sell_products = list(Product.objects.filter(available=True).order_by("-created"))
    must_sell_products = sample(must_sell_products, 4)

    post_ranking = r.zrange("post_ranking", 0, -1)
    if post_ranking:
        post_ranking_ids = [int(post_id) for post_id in post_ranking]
        most_viewed_post = list(Post.objects.filter(id__in=post_ranking_ids).exclude(id=post.id))
        most_viewed_post.sort(key=lambda x: post_ranking_ids.index(x.id))
        most_viewed_post = list(most_viewed_post)
        most_viewed_post = most_viewed_post[0]
    else:
        most_viewed_post = None
    section = post.sections.all()
    latest_posts = Post.published.all().exclude(id=post.id)[:6]
    total_views = r.incr(f"post: {post.id}:views")
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by("-same_tags", "-publish")

    context = {
        "post" : post,
        "form": form,
        "total_views": total_views,
        "similar_posts": similar_posts,
        "post_comments": post_comments,
        "comment_form" : comment_form,
        "latest_posts": latest_posts,
        "most_viewed_post": most_viewed_post,
        "must_sell_products": must_sell_products,
        "section": section
    }
    return render(request, "blog/post_details.html", context)


@login_required
def submit_comment(request, post_id):
    print(f"this is parent id : {request.POST.get('parent_id')}")
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = PostComment.objects.create(post=post, body=comment_form.cleaned_data["comment"],user=request.user)
            if request.user.is_staff:
                parent_id = request.POST.get('parent_id')
                if parent_id:
                    parent_comment = PostComment.objects.get(id=parent_id)
                    new_comment.parent = parent_comment

            new_comment.save()


    return redirect("blog:post_detail",year=post.publish.year, month=post.publish.month, day=post.publish.day, slug=post.slug)

def search_post(request, query):
    page = request.GET.get('page')
    post_only = request.GET.get('post_only')

    if query:
        form = SearchForm(request.GET)
        if form.is_valid():
            post_list = Post.published.annotate(search=SearchVector("title", "body", "subtitle")).filter(search=query)

        else:
            post_list = Post.published.annotate(search=SearchVector("title", "body", "subtitle")).filter(search=query)

        paginator = Paginator(post_list, 8)  # Show 8 posts per page

        try:
            post_list = paginator.page(page)
        except PageNotAnInteger:
            post_list = paginator.page(1)
        except EmptyPage:
            if post_only:
                return HttpResponse("")
            post_list = paginator.page(paginator.num_pages)

        context = {
            "post_list": post_list,
            "query": query,
        }

        if post_only:
            return render(request, "blog/post_list.html", context)
        else:
            return render(request, "blog/search_results.html", context)
    else:
        raise PermissionDenied


def post_by_categories(request, cat_id, slug):
    page = request.GET.get('page')
    post_only = request.GET.get('post_only')
    category = get_object_or_404(PostCategory, id=cat_id, slug=slug)
    post_list = Post.objects.filter(category=category)
    paginator = Paginator(post_list, 8)  # Show 8 posts per page
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        if post_only:
            return HttpResponse("")
        post_list = paginator.page(paginator.num_pages)

    context = {
        "post_list": post_list,
        "category":category,
    }

    if post_only:
        return render(request, "blog/post_list.html", context)
    else:
        return render(request, "blog/blog_category.html", context)

