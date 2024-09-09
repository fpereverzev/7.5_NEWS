from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Не включаем маршруты администратора и другие, требующие i18n_patterns, в основном списке urlpatterns
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('news.urls')),  # Подключение вашего приложения
    path('accounts/', include('allauth.urls')),  # Подключение маршрутов allauth
)

# Добавляем маршруты для переключения языков вне i18n_patterns
urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),  # Подключение маршрутов для переключения языка
]
