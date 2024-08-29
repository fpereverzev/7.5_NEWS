from django.shortcuts import render, redirect, get_object_or_404
from .forms import ArticleForm, PostForm
from django.contrib.auth.decorators import login_required
from .models import Category, Subscriber, Post, Article
from django.contrib import messages
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.paginator import Paginator


# Общее кэширование списка категорий
@cache_page(30)
def home(request):
    categories = cache.get('home_categories')
    if not categories:
        categories = Category.objects.all()
        cache.set('home_categories', categories, timeout=60)
    return render(request, 'default.html', {'categories': categories})


@login_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save()
            messages.success(request, "Статья успешно создана.")
            return redirect('articles:list')  # Замените на правильный путь
        else:
            messages.error(request, "Ошибка при создании статьи.")
    else:
        form = ArticleForm()

    # Передаем категории в шаблон
    categories = Category.objects.all()
    return render(request, 'news/create_article.html', {'form': form, 'categories': categories})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            messages.success(request, "Пост успешно создан.")
            cache.set(f'post_{post.id}', post, timeout=None)  # Кэшируем пост
            return redirect('news:post_list')  # Замените на правильный путь
        else:
            messages.error(request, "Ошибка при создании поста.")
    else:
        form = PostForm()

    # Передаем категории в шаблон
    categories = Category.objects.all()
    return render(request, 'news/create_post.html', {'form': form, 'categories': categories})


@login_required
def manage_subscription(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        selected_categories = request.POST.getlist('categories')
        Subscriber.objects.filter(user=request.user).delete()
        for category_id in selected_categories:
            category = get_object_or_404(Category, id=category_id)
            Subscriber.objects.create(user=request.user, category=category)
        messages.success(request, "Подписки успешно обновлены.")
        return redirect('news:subscriptions')  # Замените на правильный путь

    user_subscriptions = Subscriber.objects.filter(user=request.user).values_list('category_id', flat=True)
    return render(request, 'news/subscriptions.html',
                  {'categories': categories, 'user_subscriptions': user_subscriptions})


@cache_page(30)
def news_detail(request, news_id):
    post = cache.get(f'post_{news_id}')
    if not post:
        post = get_object_or_404(Post, id=news_id)
        cache.set(f'post_{news_id}', post, timeout=300)
    return render(request, 'news/news_detail.html', {'post': post})


@cache_page(30)
def article_detail(request, article_id):
    article = cache.get(f'article_{article_id}')
    if not article:
        article = get_object_or_404(Article, id=article_id)
        cache.set(f'article_{article_id}', article, timeout=300)
    return render(request, 'news/article_detail.html', {'article': article})


def category_articles(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    articles = Article.objects.filter(category=category)
    return render(request, 'news/category_articles.html', {'category': category, 'articles': articles})


def post_list(request):
    posts = Post.objects.all().order_by('-dateCreation')
    paginator = Paginator(posts, 10)  # Показывать 10 постов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/post_list.html', {'page_obj': page_obj})


def article_list(request):
    articles = Article.objects.all().order_by('-published_date')
    paginator = Paginator(articles, 10)  # Показывать 10 статей на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/article_list.html', {'page_obj': page_obj})
