from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import Article, Post

def create_authors_group():
    # Проверка, существует ли группа
    group, created = Group.objects.get_or_create(name='authors')

    # Получение типов контента для моделей Article и Post
    article_ct = ContentType.objects.get_for_model(Article)
    post_ct = ContentType.objects.get_for_model(Post)

    # Получение необходимых разрешений
    permissions = Permission.objects.filter(
        content_type__in=[article_ct, post_ct],
        codename__in=['add_article', 'change_article', 'add_post', 'change_post']
    )

    # Добавление разрешений группе
    for permission in permissions:
        group.permissions.add(permission)

    print("Группа 'authors' настроена успешно.")

# Запуск функции
create_authors_group()
