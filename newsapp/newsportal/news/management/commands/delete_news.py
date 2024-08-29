from django.core.management.base import BaseCommand
from news.models import Post, Category

class Command(BaseCommand):
    help = 'Удаляет все новости из указанной категории после подтверждения'

    def add_arguments(self, parser):
        parser.add_argument('category', type=str, help='Название категории, из которой будут удалены все новости')

    def handle(self, *args, **options):
        category_name = options['category']
        answer = input(f'Вы действительно хотите удалить все новости из категории "{category_name}"? (yes/no): ').strip().lower()

        if answer != 'yes':
            self.stdout.write(self.style.ERROR('Операция отменена'))
            return

        try:
            category = Category.objects.get(name=category_name)
            num_deleted, _ = Post.objects.filter(category=category).delete()
            self.stdout.write(self.style.SUCCESS(f'Успешно удалено {num_deleted} новостей из категории "{category_name}"'))
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Категория "{category_name}" не найдена'))
