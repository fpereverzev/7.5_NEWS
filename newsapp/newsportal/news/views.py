from django.shortcuts import render, redirect, get_object_or_404
from .forms import ArticleForm, PostForm
from django.contrib.auth.decorators import login_required
from .models import Category, Subscriber, Post, Article, Author, PostCategory  # Добавьте PostCategory сюда
from django.contrib import messages
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from django.http import Http404


def home(request):
    categories = Category.objects.all()
    post_categories = PostCategory.objects.all()  # Получаем категории постов

    # Получаем все посты и группируем их по категориям
    posts_by_category = {}
    for category in post_categories:
        posts_by_category[category] = Post.objects.filter(categories=category)

    return render(request, 'news/default.html', {
        'categories': categories,
        'post_categories': post_categories,  # Передаем категории постов в шаблон
        'posts_by_category': posts_by_category,  # Передаем посты по категориям в шаблон
    })


@login_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user  # Присваиваем автора статьи
            article.save()
            messages.success(request, "Статья успешно создана.")
            return redirect('news:article_list')
        else:
            messages.error(request, "Ошибка при создании статьи.")
    else:
        form = ArticleForm()

    categories = Category.objects.all()
    return render(request, 'news/create_article.html', {'form': form, 'categories': categories})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            # Проверяем, есть ли автор для текущего пользователя
            author, created = Author.objects.get_or_create(authorUser=request.user)
            post = form.save(commit=False)
            post.author = author
            post.save()
            messages.success(request, "Пост успешно создан.")
            return redirect('news:post_list')
        else:
            messages.error(request, "Ошибка при создании поста.")
    else:
        form = PostForm()

    return render(request, 'news/create_post.html', {'form': form})


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
        return redirect('news:subscriptions')

    user_subscriptions = Subscriber.objects.filter(user=request.user).values_list('category_id', flat=True)
    return render(request, 'news/subscriptions.html',
                  {'categories': categories, 'user_subscriptions': user_subscriptions})


def news_detail(request, post_id):
    post = cache.get(f'post_{post_id}')
    if not post:
        post = get_object_or_404(Post, id=post_id)
        cache.set(f'post_{post_id}', post, timeout=300)
    return render(request, 'news/news_detail.html', {'post': post})


def article_detail(request, article_id):
    article = cache.get(f'article_{article_id}')
    if not article:
        article = get_object_or_404(Article, id=article_id)
        if article.is_deleted:
            raise Http404("Article does not exist")
        cache.set(f'article_{article_id}', article, timeout=5 * 60)
    return render(request, 'news/article_detail.html', {'article': article})


def category_articles(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    articles = Article.objects.filter(category=category, is_deleted=False)
    return render(request, 'news/category_articles.html', {'category': category, 'articles': articles})


def post_category_articles(request, post_category_id):
    post_category = get_object_or_404(PostCategory, id=post_category_id)
    posts = Post.objects.filter(categories=post_category).order_by('-dateCreation')
    return render(request, 'news/post_category_articles.html', {
        'post_category': post_category,
        'posts': posts
    })


def post_list(request):
    posts = Post.objects.all().order_by('-dateCreation')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/post_list.html', {'page_obj': page_obj})


def article_list(request):
    articles = Article.objects.filter(is_deleted=False).order_by('-published_date')
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/article_list.html', {'page_obj': page_obj})


@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.user == article.author or request.user.is_superuser:
        article.is_deleted = True
        article.save()  # Сохраняем изменения
        messages.success(request, "Статья успешно удалена.")
        return redirect('news:article_list')
    else:
        messages.error(request, "У вас нет прав на удаление этой статьи.")
        return redirect('news:article_detail', article_id=article.id)


@login_required
def update_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.user != article.author and not request.user.is_superuser:
        messages.error(request, "У вас нет прав на редактирование этой статьи.")
        return redirect('news:article_detail', article_id=article.id)

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Статья успешно обновлена.")
            return redirect('news:article_detail', article_id=article.id)
        else:
            messages.error(request, "Ошибка при обновлении статьи.")
    else:
        form = ArticleForm(instance=article)

    return render(request, 'news/update_article.html', {'form': form, 'article': article})


@login_required
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author.authorUser and not request.user.is_superuser:
        messages.error(request, "У вас нет прав на редактирование этого поста.")
        return redirect('news:news_detail', post_id=post.id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Пост успешно обновлен.")
            return redirect('news:news_detail', post_id=post.id)
        else:
            messages.error(request, "Ошибка при обновлении поста.")
    else:
        form = PostForm(instance=post)

    return render(request, 'news/update_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author.authorUser or request.user.is_superuser:
        post.delete()
        messages.success(request, "Пост успешно удален.")
        return redirect('news:post_list')
    else:
        messages.error(request, "У вас нет прав на удаление этого поста.")
        return redirect('news:news_detail', post_id=post.id)


@login_required
def confirm_delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author.authorUser and not request.user.is_superuser:
        messages.error(request, "У вас нет прав на удаление этого поста.")
        return redirect('news:news_detail', post_id=post.id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Пост успешно удален.")
        return redirect('news:post_list')

    return render(request, 'news/confirm_delete_post.html', {'post': post})


class RegisterView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_mail(
                'Успешная регистрация',
                'Вы успешно зарегистрировались на нашем сайте!',
                'sfexample123@yandex.ru',
                [user.email],
                fail_silently=False,
            )
            messages.success(request, "Регистрация прошла успешно! Письмо отправлено на ваш email.")
            return redirect('login')
        return render(request, 'registration/register.html', {'form': form})
