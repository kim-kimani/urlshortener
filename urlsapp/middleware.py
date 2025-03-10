from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.conf import settings

class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            # Extend session duration for admin users
            request.session.set_expiry(365 * 24 * 60 * 60)  # 1 year
        elif not request.user.is_authenticated:
            # Check if the user is logged into the admin panel
            admin_user = User.objects.filter(is_staff=True).first()
            if admin_user and request.path.startswith('/admin/') and request.session.get('admin_logged_in'):
                login(request, admin_user)
                request.session.set_expiry(365 * 24 * 60 * 60)  # 1 year

        response = self.get_response(request)
        return response