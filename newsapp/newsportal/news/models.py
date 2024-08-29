from django.db import models
from django.db.models import Sum, F
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from .tasks import send_notification


# Модель для создания статьи
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)  # Сделать опциональным

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.set(f'article_{self.id}', self, timeout=None)  # Кэшируем статью без таймаута

    def delete(self, *args, **kwargs):
        cache.delete(f'article_{self.id}')
        super().delete(*args, **kwargs)


@receiver(post_save, sender=Article)
def clear_cache_on_article_save(sender, instance, **kwargs):
    cache.set(f'article_{instance.id}', instance, timeout=None)


@receiver(post_delete, sender=Article)
def clear_cache_on_article_delete(sender, instance, **kwargs):
    cache.delete(f'article_{instance.id}')


# Модель для авторов
class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    def update_rating(self):
        postRat = self.post_set.aggregate(postRating=Sum('rating'))
        pRat = postRat.get('postRating', 0) or 0

        commentRat = self.authorUser.comment_set.aggregate(commentRating=Sum('rating'))
        cRat = commentRat.get('commentRating', 0) or 0

        self.ratingAuthor = pRat * 3 + cRat
        self.save()


# Модель для категорий

# Модель для постов
class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )
    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    dateCreation = models.DateTimeField(auto_now_add=True)
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
    if created and instance.categoryType == Post.NEWS:
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
    dateCreation = models.DateTimeField(auto_now_add=True)
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
