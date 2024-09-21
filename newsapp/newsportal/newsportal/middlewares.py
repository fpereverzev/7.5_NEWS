from django.utils import timezone
import pytz
from news.models import UserProfile


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Попытка получить профиль пользователя
                user_timezone = request.user.userprofile.timezone
            except UserProfile.DoesNotExist:
                # Если профиль не существует, создаём его с UTC как зоной по умолчанию
                user_timezone = 'UTC'
                UserProfile.objects.create(user=request.user, timezone=user_timezone)
        else:
            user_timezone = 'UTC'

        # Активация временной зоны пользователя
        timezone.activate(pytz.timezone(user_timezone))
        response = self.get_response(request)
        timezone.deactivate()
        return response
