from django.utils.deprecation import MiddlewareMixin

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