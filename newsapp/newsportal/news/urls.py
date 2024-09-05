from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.home, name='home'),
    path('articles/create/', views.create_article, name='create_article'),
    path('posts/create/', views.create_post, name='create_post'),
    path('subscriptions/', views.manage_subscription, name='subscriptions'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('articles/<int:article_id>/', views.article_detail, name='article_detail'),
    path('category/<int:category_id>/', views.category_articles, name='category_articles'),
    path('articles/', views.article_list, name='article_list'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('articles/<int:article_id>/delete/', views.delete_article, name='delete_article'),
    path('articles/<int:article_id>/update/', views.update_article, name='update_article'),
    path('post-category/<int:post_category_id>/', views.post_category_articles, name='post_category_articles'),
]
