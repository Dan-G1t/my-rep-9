from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Author
from .filters import PostFilter
from .forms import PostForm 
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse  # Для обработки ошибок
from django.core.exceptions import ValidationError


class PostsList(ListView):
    model = Post
    ordering = '-creation_date'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 9


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = self.object.category.all()
        return context
    
    
    def post(self, request, *args, **kwargs):
        post = self.get_object()
        category = post.category.first()  # Получаем все категории новости
        
        if request.user.is_authenticated:
            if category:
                if request.user in category.subscribers.all():
                    category.subscribers.remove(request.user)
                else:
                    category.subscribers.add(request.user)
            return self.get(request, *args, **kwargs)  # Возвращаем к странице поста
        else:
            return redirect('/accounts/login/')  # Перенаправляем неавторизованного пользователя на страницу авторизации
    

class PostSearch(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
       queryset = super().get_queryset()
       self.filterset = PostFilter(self.request.GET, queryset)
       return self.filterset.qs

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['filterset'] = self.filterset
       return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news_portal.add_post', )
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = Author.objects.get(user=self.request.user)
        try:
            post.save()
            form.save_m2m()
            #post.send_notifications()
            return super().form_valid(form)
        except ValidationError as e:
            return HttpResponse(e.messages[0])
    

class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news_portal.change_post', )
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news_portal.delete_post', )
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

