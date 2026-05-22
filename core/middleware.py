from django.contrib.auth import logout

from .admin_roles import is_admin_identity


class AdminPortalIsolationMiddleware:
    """End admin sessions if they leave the operations portal."""

    allowed_prefixes = (
        '/admin-portal',
        '/admin/',
        '/login/',
        '/logout/',
        '/static/',
        '/media/',
        '/favicon.ico',
        '/.well-known/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if is_admin_identity(request.user) and not request.path.startswith(self.allowed_prefixes):
            logout(request)
        return self.get_response(request)
