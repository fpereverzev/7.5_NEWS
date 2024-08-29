# news/tasks.py

from django.apps import apps
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
import datetime

@shared_task
def send_notification(news_id):
    News = apps.get_model('news', 'News')
    Subscriber = apps.get_model('news', 'Subscriber')

    try:
        news = News.objects.get(id=news_id)
        subscribers = Subscriber.objects.all()
        for subscriber in subscribers:
            send_mail(
                subject=f'New News: {news.title}',
                message=news.content,
                from_email='from@example.com',
                recipient_list=[subscriber.email],
                fail_silently=False,
            )
    except News.DoesNotExist:
        pass

@shared_task
def weekly_newsletter():
    News = apps.get_model('news', 'News')
    Subscriber = apps.get_model('news', 'Subscriber')

    last_week = timezone.now() - datetime.timedelta(days=7)
    news_list = News.objects.filter(created_at__gte=last_week)
    if news_list.exists():
        for subscriber in Subscriber.objects.all():
            message = "\n".join([f"{news.title}: {news.content}" for news in news_list])
            send_mail(
                subject='Weekly News Update',
                message=message,
                from_email='from@example.com',
                recipient_list=[subscriber.email],
                fail_silently=False,
            )
