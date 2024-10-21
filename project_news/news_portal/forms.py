from django import forms
from .models import Post, Category
from django.core.exceptions import ValidationError


class PostForm(forms.ModelForm):
    text = forms.CharField(min_length=300, label='Основной текст')
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple, label='Выбор категории')

    class Meta:
        model = Post
        fields = [
            'content_type',
            'title',
            'text',
            'category',
        ]
        labels = {
            'content_type': 'Тип публикации',
            'title': 'Заголовок',
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        text = cleaned_data.get("text")
        
        if title == text:
            raise ValidationError("Текст не должен совпадать с заголовком.")
        
        return cleaned_data


