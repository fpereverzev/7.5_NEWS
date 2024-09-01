from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('news.urls')),  # Подключение вашего приложения
    path('accounts/', include('allauth.urls')),  # Подключение маршрутов allauth
]
