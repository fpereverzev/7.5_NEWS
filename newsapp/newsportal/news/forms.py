from django import forms
from .models import Article, Category, Post
from allauth.account.forms import SignupForm


class ArticleForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),  # Изначально пустой queryset
        required=True,
        empty_label="Выберите категорию"
    )

    class Meta:
        model = Article
        fields = ['title', 'content', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()  # Динамически получаем категории


class PostForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'categories']


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='Имя', required=True)
    last_name = forms.CharField(max_length=30, label='Фамилия', required=True)

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user
