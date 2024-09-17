from django.contrib import admin
from .models import Category, Post, Article
from modeltranslation.admin import TranslationAdmin


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'title']
    list_filter = ('author', 'categories')
    search_fields = ('name', 'time_in')


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date')
    list_filter = ('author', 'published_date', 'category')
    search_fields = ('title', 'content')


class TransCategoryAdmin(TranslationAdmin):
    model = Category


class TransPostAdmin(PostAdmin, TranslationAdmin):
    model = Post


class TransArticleAdmin(ArticleAdmin, TranslationAdmin):
    model = Article


admin.site.register(Category, TransCategoryAdmin)
admin.site.register(Post, TransPostAdmin)
admin.site.register(Article, TransArticleAdmin)
