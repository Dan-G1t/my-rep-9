from django import template


register = template.Library()


bad_words = ['редиска', 'негодяй', 'дурак', 'балбес', 'волан-де-морт', 'Редиска', 'Негодяй', 'Дурак', 'Балбес', 'Волан-де-морт']


@register.filter()
def censor(text):
    if isinstance(text, str):
        for word in bad_words:
            text = text.replace(word, word[0] + '*' * (len(word) - 1))
        return text
    else:
        raise TypeError("Фильтр censor() должен получить строку.")