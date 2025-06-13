from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render
import re

class MobileDeviceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self.is_mobile(request):
            return render(request, 'game/mobile_blocked.html')
        return self.get_response(request)

    def is_mobile(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        mobile_patterns = [
            'Mobile', 'Android', 'iPhone', 'iPad', 'Windows Phone',
            'webOS', 'BlackBerry', 'iPod'
        ]
        return any(pattern in user_agent for pattern in mobile_patterns)

class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    """
    Middleware to add Content Security Policy headers to responses.
    """
    def process_response(self, request, response):
        # Add CSP header to allow 'self' and necessary external resources
        # Include 'unsafe-eval' to allow setTimeout with string arguments
        csp_value = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )
        
        response["Content-Security-Policy"] = csp_value
        return response