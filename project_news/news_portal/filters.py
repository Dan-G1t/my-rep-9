from django_filters import FilterSet, DateFilter, CharFilter, ModelChoiceFilter
from .models import Post, Category
from django import forms


class PostFilter(FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains',  label='Поиск по заголовку:')
    category = ModelChoiceFilter(field_name='category', queryset=Category.objects.all(),  label='Выбор категории:', empty_label='Все категории')
    creation_date = DateFilter(field_name='creation_date', lookup_expr='gt', widget=forms.DateInput(attrs={'type': 'date'}), label='Позже указанной даты:'
)