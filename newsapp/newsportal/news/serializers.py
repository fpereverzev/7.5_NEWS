from rest_framework import serializers
from .models import Article, Post, Category


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'published_date',]  # Явно указывайте поля

    def validate_title(self, value):
        if Article.objects.filter(title=value).exists():
            raise serializers.ValidationError("Статья с таким заголовком уже существует.")
        return value


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'text', 'author', 'date_creation',]  # Явно указывайте поля
