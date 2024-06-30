from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from .models import Profile

User = get_user_model()

class OneSessionPerUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            profile = Profile.objects.get(profile=request.user)
            session_key = request.session.session_key
            if profile.session_key and profile.session_key != session_key:
                request.session.flush()
            profile.session_key = session_key
            profile.save()
