from .models import Post
from django.db.models.signals import post_save, pre_save
from django.core.mail import send_mail
from django.dispatch import receiver
from django.core.signals import request_finished
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string 


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    categories = instance.category.all()
    for category in categories:
        # Получаем подписчиков на категорию
        subscribers = category.subscribers.all()
        # Уведомляем каждого подписчика
        for subscriber in subscribers:
            # HTML-рассылка
            html_content = render_to_string('email_notification.html', {
            'title': instance.title,
            'text': instance.text,
            'username': subscriber.username,
            'id': instance.id
        })
            msg = EmailMultiAlternatives(
                subject=instance.title,
                body=f'Здравствуй, {subscriber.username}. Новая статья в твоём любимом разделе!',
                from_email='gdaprog@yandex.ru',
                to=[subscriber.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()


@receiver(pre_save, sender=Post)
def check_news_limit(sender, instance, **kwargs):
    # Получаем сегодняшнюю дату без времени
    today = timezone.now().date()
    # Подсчитываем количество новостей, опубликованных пользователем сегодня
    posts_count_today = Post.objects.filter(author=instance.author, creation_date__date=today).count()
    # Если превышен лимит, запускаем ошибку
    if posts_count_today > 3:
        raise ValidationError("Вы достигли лимита публикаций новостей на сегодня.")