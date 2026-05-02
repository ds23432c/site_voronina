from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db.models import Count, F, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ForumCommentForm, ForumPostForm
from .models import ForumCategory, ForumComment, ForumPost


def _is_admin(user):
    return bool(getattr(user, "is_authenticated", False) and getattr(user, "role", "") == "admin")


def _can_edit_post(user, post):
    return user.is_authenticated and (post.author_id == user.id or _is_admin(user))


def index(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    posts = (
        ForumPost.objects.select_related("author")
        .prefetch_related("categories")
        .filter(is_published=True)
    )

    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(content__icontains=query))

    if category_slug:
        posts = posts.filter(categories__slug=category_slug)

    posts = posts.annotate(comments_count=Count("comments")).distinct().order_by("-created_at")
    categories = ForumCategory.objects.annotate(posts_count=Count("posts")).order_by("name")
    top_posts = (
        ForumPost.objects.filter(is_published=True)
        .select_related("author")
        .annotate(comments_count=Count("comments"))
        .order_by("-likes_count", "-views_count")[:5]
    )

    return render(
        request,
        "forum/index.html",
        {
            "posts": posts,
            "categories": categories,
            "top_posts": top_posts,
            "query": query,
            "selected_category": category_slug,
        },
    )


def detail(request, slug):
    post = get_object_or_404(
        ForumPost.objects.select_related("author").prefetch_related("categories", "comments__author"),
        slug=slug,
        is_published=True,
    )

    if request.method == "GET":
        ForumPost.objects.filter(pk=post.pk).update(views_count=F("views_count") + 1)
        post.refresh_from_db(fields=["views_count"])

    comment_form = ForumCommentForm()
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.path)
        comment_form = ForumCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Комментарий опубликован.")
            return redirect(post.get_absolute_url())

    return render(
        request,
        "forum/detail.html",
        {
            "post": post,
            "comment_form": comment_form,
            "can_edit": _can_edit_post(request.user, post),
        },
    )


@login_required
def post_create(request):
    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, "Тема форума опубликована.")
            return redirect(post.get_absolute_url())
    else:
        form = ForumPostForm()
    return render(request, "forum/post_form.html", {"form": form, "mode": "create"})


@login_required
def post_edit(request, slug):
    post = get_object_or_404(ForumPost, slug=slug)
    if not _can_edit_post(request.user, post):
        raise Http404

    if request.method == "POST":
        form = ForumPostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if not post.author_id:
                post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, "Тема обновлена.")
            return redirect(post.get_absolute_url())
    else:
        form = ForumPostForm(instance=post)

    return render(request, "forum/post_form.html", {"form": form, "mode": "edit", "post": post})


@require_POST
def like_post(request, slug):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "detail": "authentication_required"}, status=403)

    post = get_object_or_404(ForumPost, slug=slug, is_published=True)
    ForumPost.objects.filter(pk=post.pk).update(likes_count=F("likes_count") + 1)
    post.refresh_from_db(fields=["likes_count"])
    return JsonResponse({"ok": True, "likes_count": post.likes_count})


@require_POST
def comment_like(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "detail": "authentication_required"}, status=403)

    comment = get_object_or_404(ForumComment, pk=pk)
    ForumComment.objects.filter(pk=comment.pk).update(likes_count=F("likes_count") + 1)
    comment.refresh_from_db(fields=["likes_count"])
    return JsonResponse({"ok": True, "likes_count": comment.likes_count})