# Generated by Django 5.0.4 on 2024-09-19 18:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0018_article_content_en_article_content_ru_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='author',
            old_name='authorUser',
            new_name='author_user',
        ),
        migrations.RenameField(
            model_name='author',
            old_name='ratingAuthor',
            new_name='rating_author',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='dateCreation',
            new_name='date_creation',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='categoryType',
            new_name='category_type',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='dateCreation',
            new_name='date_creation',
        ),
    ]
