from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from posts.forms import PostForm
from posts.models import Group, Post, User
from posts.utils import get_page

LIMIT = 10


def index(request):
    """Метод отображения главной страницы сайта."""
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = get_page(request, posts, LIMIT)
    context = {
        'page_obj': page_obj,
        'posts': posts
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Метод отображения страницы с постами группы."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page(request, posts, LIMIT)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Метод отображения страницы профиля пользователя."""
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    page_obj = get_page(request, posts, LIMIT)
    count_posts = posts.count()
    context = {
        'username': user,
        'posts': posts,
        'page_obj': page_obj,
        'count_posts': count_posts,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Метод отображения страницы с описанием поста."""
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        pk=post_id
    )
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создание новой записи."""
    template = 'posts/create_post.html'
    user = get_user(request)
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            return redirect('posts:profile', user.username)
    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирование записи."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    context = {
        'post': post,
        'is_edit': True,
        'form': form
    }
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    if post.author == request.user:
        return render(request, template, context)
    else:
        return redirect('posts:post_detail', post_id)
