from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Ваши маршруты без i18n
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('news.urls')),  # Подключение вашего приложения
    path('accounts/', include('allauth.urls')),  # Подключение маршрутов allauth
)

# Маршруты для переключения языков
urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),  # Подключение маршрутов для переключения языка
]
