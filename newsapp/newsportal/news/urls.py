from django.urls import path
from . import views
from .views import NewsListCreateView, NewsDetailView, ArticleListCreateView, ArticleDetailView

app_name = 'news'

urlpatterns = [
    path('', views.home, name='home'),
    path('articles/create/', views.create_article, name='create_article'),
    path('posts/create/', views.create_post, name='create_post'),
    path('subscriptions/', views.manage_subscription, name='subscriptions'),
    path('posts/<int:post_id>/', views.news_detail, name='news_detail'),
    path('articles/<int:article_id>/', views.article_detail, name='article_detail'),
    path('category/<int:category_id>/', views.category_articles, name='category_articles'),
    path('articles/', views.article_list, name='article_list'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('articles/<int:article_id>/delete/', views.delete_article, name='delete_article'),
    path('articles/<int:article_id>/update/', views.update_article, name='update_article'),
    path('post-category/<int:post_category_id>/', views.post_category_articles, name='post_category_articles'),
    path('posts/', views.post_list, name='post_list'),
    path('post/<int:post_id>/confirm-delete/', views.confirm_delete_post, name='confirm_delete_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('timezone/change/', views.change_timezone, name='timezone_change'),

    path('api/news/', NewsListCreateView.as_view(), name='api_news_list_create'),  # для GET и POST новостей
    path('api/news/<int:pk>/', NewsDetailView.as_view(), name='api_news_detail'),  # для GET, PUT, DELETE одной новости
    path('api/articles/', ArticleListCreateView.as_view(), name='api_article_list_create'),  # для GET и POST статей
    path('api/articles/<int:pk>/', ArticleDetailView.as_view(), name='api_article_detail'),

]
