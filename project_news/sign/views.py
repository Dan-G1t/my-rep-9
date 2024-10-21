from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from news_portal.models import Author

@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    # Проверяем, состоит ли пользователь уже в группе авторов
    if not request.user.groups.filter(name='authors').exists():
        # Добавляем пользователя в группу
        authors_group.user_set.add(user)
        # Создаем объект Author, если его еще нет
        Author.objects.get_or_create(user=user)
    return redirect('/accounts/profile/')