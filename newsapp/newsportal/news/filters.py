import django_filters
from django_filters import FilterSet, DateTimeFilter
from django.forms import DateTimeInput
from .models import Article

class NewsFilter(FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Title')
    category = django_filters.CharFilter(lookup_expr='icontains', label='Category')
    published_after = DateTimeFilter(
        field_name='published_date',
        lookup_expr='gt',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
        label='Published after'
    )

    class Meta:
        model = Article
        fields = ['title', 'category', 'published_after']
