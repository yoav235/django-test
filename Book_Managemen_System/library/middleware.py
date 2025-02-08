import jwt
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.middleware.csrf import get_token

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = None  # Default: No user
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                request.user = User.objects.filter(id=payload["id"]).first()
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token expired"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "Invalid token"}, status=401)

        response = self.get_response(request)

        # 🔹 Get CSRF token
        csrf_token = get_token(request)

        # 🔹 Set CSRF token in headers and cookie
        response.set_cookie("csrftoken", csrf_token, httponly=False, secure=False, samesite="Lax")
        response["X-CSRFToken"] = csrf_token  # 🔹 Add CSRF token to the headers

        return response
