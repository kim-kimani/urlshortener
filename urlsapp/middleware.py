from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


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
    
class RobotsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 200 and "text/html" in response.get('Content-Type', ''):
            response.content = response.content.replace(
                b'</head>',
                b'<meta name="robots" content="noindex, nofollow, noarchive, nosnippet"></head>'
            )
        return response
    
class XRobotsTagMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Robots-Tag"] = "noindex, nofollow, noarchive, nosnippet"
        return response