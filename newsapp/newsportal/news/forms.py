from django import forms
from .models import Article, Category, Post


class ArticleForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        empty_label="Выберите категорию"
    )

    class Meta:
        model = Article
        fields = ['title', 'content', 'category']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['author', 'categoryType', 'title', 'text']
