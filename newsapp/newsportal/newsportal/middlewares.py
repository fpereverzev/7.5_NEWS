# newsportal/middlewares.py
from django.utils import timezone
import pytz


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_timezone = request.user.userprofile.timezone if request.user.is_authenticated else 'UTC'
        timezone.activate(pytz.timezone(user_timezone))
        response = self.get_response(request)
        timezone.deactivate()
        return response
