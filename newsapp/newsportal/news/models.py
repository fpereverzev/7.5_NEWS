from django.db import models
from django.db.models import Sum, F
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from .tasks import send_notification

# Модель для категорий
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# Модель для статей
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Удалено значение по умолчанию

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.set(f'article_{self.id}', self, timeout=None)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

@receiver(post_save, sender=Article)
def clear_cache_on_article_save(sender, instance, **kwargs):
    cache.set(f'article_{instance.id}', instance, timeout=None)

@receiver(post_delete, sender=Article)
def clear_cache_on_article_delete(sender, instance, **kwargs):
    cache.delete(f'article_{instance.id}')

# Модель для авторов
class Author(models.Model):
    author_user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating_author = models.SmallIntegerField(default=0)

    def update_rating(self):
        post_rating = self.author_user.post_set.aggregate(postRating=Sum('rating'))
        p_rat = post_rating.get('postRating', 0) or 0

        comment_rating = self.author_user.comment_set.aggregate(commentRating=Sum('rating'))
        c_rat = comment_rating.get('commentRating', 0) or 0

        self.rating_author = p_rat * 3 + c_rat
        self.save()

# Модель для постов
class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )
    category_type = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    date_creation = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory', related_name='posts')
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating = F('rating') + 1
        self.save(update_fields=['rating'])

    def dislike(self):
        self.rating = F('rating') - 1
        self.save(update_fields=['rating'])

    def preview(self):
        return f'{self.text[:123]} ... {self.rating}'

    def __str__(self):
        return self.title

@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created and instance.category_type == Post.NEWS:
        send_notification.delay(instance.id)

# Модель для связи постов и категорий
class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'category')

    def __str__(self):
        return f"{self.post.title} - {self.category.name}"

# Модель для комментариев
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating = F('rating') + 1
        self.save(update_fields=['rating'])

    def dislike(self):
        self.rating = F('rating') - 1
        self.save(update_fields=['rating'])

    def preview(self):
        return f'{self.text[:123]} ... {self.rating}'

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

# Модель для подписчиков на категории
class Subscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'category')

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"
