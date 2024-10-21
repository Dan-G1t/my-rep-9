import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils import timezone
from django.core.mail import send_mail
from news_portal.models import Post, Category
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string 
 
 
logger = logging.getLogger(__name__)
 
# наша задача по рассылке сообщений подписчикам
def my_job():
    now = timezone.now()
    last_week = now - timezone.timedelta(days=7)
    new_posts = Post.objects.filter(creation_date__gt=last_week)
    
    # Получаем всех подписчиков и связанные с ними категории
    categories = Category.objects.prefetch_related('subscribers')

    # Словарь для хранения новых постов для каждого подписчика
    subscribers_posts = {}

    # Для каждой категории проверяем подписчиков
    for category in categories:
        # Получаем подписчиков категории
        subscribers = category.subscribers.all()
        
        # Фильтруем новые посты по этой категории
        category_posts = new_posts.filter(category=category)

        if category_posts.exists():  # Проверяем, есть ли новые посты в категории
            for subscriber in subscribers:
                if subscriber not in subscribers_posts:
                    subscribers_posts[subscriber] = []
                
                # Добавляем посты в список этого подписчика
                subscribers_posts[subscriber].extend(category_posts)

    # Отправка писем всем подписчикам
    for subscriber, posts in subscribers_posts.items():
        # Удаляем дубликаты постов, если есть несколько подписок
        unique_posts = {post.id: post for post in posts}.values()

        # Готовим HTML содержимое
        html_content = render_to_string('email_notification_week.html', {
            'username': subscriber.username,
            'posts': unique_posts,
        })

        msg = EmailMultiAlternatives(
            subject='Новые статьи за неделю',
            body=f'Здравствуй, {subscriber.username}! Собрали подборку статей за неделю из твоих любимых разделов!',
            from_email='gdaprog@yandex.ru',
            to=[subscriber.email],
        )

        msg.attach_alternative(html_content, "text/html")
        msg.send()

 
# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
 
 
class Command(BaseCommand):
    help = "Runs apscheduler."
 
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            #Будет выполняться каждую неделю в воскресенье в 17:00:
            trigger=CronTrigger(day_of_week="sun", hour="17", minute="00"), 
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")
 
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )
 
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")