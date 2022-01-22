from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow


def authorized_only(func):
    # Декоратор для проверки авторизован ли пользователь
    def check_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return redirect('/auth/login/')

    return check_user


def index(request: HttpRequest) -> HttpResponse:
    # Домашняя страница
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PER_PAGE_PAGINATOR)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    template_name = 'posts/index.html'
    return render(request, template_name, context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    # Страница постов группы
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups_posts.all()
    paginator = Paginator(posts, settings.PER_PAGE_PAGINATOR)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'slug': slug,
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    template_name = 'posts/group_list.html'
    return render(request, template_name, context=context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    # Страница профайла пользователя
    username = get_object_or_404(User, username=username)
    post_list = username.posts.all()
    following = username.following.exists()
    paginator = Paginator(post_list, settings.PER_PAGE_PAGINATOR)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'username': username,
        'post_list': post_list,
        'page_obj': page_obj,
        'following': following,
    }
    template_name = 'posts/profile.html'
    return render(request, template_name, context=context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    # Страница поста
    post = get_object_or_404(Post, pk=post_id)
    post_text = get_object_or_404(Post, id=post_id).text[:30]
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm()
    context = {
        'post': post,
        'post_text': post_text,
        'comments': comments,
        'form': form,
    }
    template_name = 'posts/post_detail.html'
    return render(request, template_name, context)


@authorized_only
def post_create(request: HttpRequest) -> HttpResponse:
    # Страница создания поста
    is_edit = False
    title = 'Добавить запись'
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.pub_date = timezone.now()
        post.save()
        return redirect('posts:profile', username=post.author.username)
    context = {
        'form': form,
        'is_edit': is_edit,
        'title': title,
    }
    template_name = 'posts/create_post.html'
    return render(request, template_name, context)


@authorized_only
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    # Страница редактирования поста
    post = get_object_or_404(Post, id=post_id)
    author = post.author.username
    group = post.group
    is_edit = True
    title = 'Редактировать запись'
    if request.user.username == author:
        if request.method == "POST":
            form = PostForm(request.POST or None,
                            files=request.FILES or None,
                            instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.pub_date = timezone.now()
                post.save()
                return redirect('posts:post_detail', post_id=post.pk)
        else:
            form = PostForm(instance=post)
        context = {
            'form': form,
            'group': group,
            'is_edit': is_edit,
            'title': title,
        }
        template_name = 'posts/create_post.html'
        return render(request, template_name, context)
    else:
        template_name = 'posts:post_detail'
        return redirect(template_name, post_id=post.pk)


@authorized_only
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@authorized_only
def follow_index(request: HttpRequest) -> HttpResponse:
    # Страница подписки
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    post_list = Post.objects.filter(author__id__in=authors)
    paginator = Paginator(post_list, settings.PER_PAGE_PAGINATOR)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Посты авторов, на которых вы подписаны'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    template_name = 'posts/follow.html'
    return render(request, template_name, context)


@authorized_only
def profile_follow(request, username):
    # Подписаться на автора
    author = User.objects.get(username=username)
    user = request.user
    if author != user and (author.following.count() == 0):
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=username)


@authorized_only
def profile_unfollow(request, username):
    # Дизлайк, отписка
    user = request.user
    Follow.objects.get(user=user, author__username=username).delete()
    return redirect('posts:profile', username=username)
