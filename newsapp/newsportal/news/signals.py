from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from .models import Post, Article, Category
from .tasks import send_notification

@receiver(post_save, sender=Article)
def clear_cache_on_article_save(sender, instance, **kwargs):
    cache.set(f'article_{instance.id}', instance, timeout=None)

@receiver(post_delete, sender=Article)
def clear_cache_on_article_delete(sender, instance, **kwargs):
    cache.delete(f'article_{instance.id}')

@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created and instance.categoryType == Post.NEWS:
        send_notification.delay(instance.id)
