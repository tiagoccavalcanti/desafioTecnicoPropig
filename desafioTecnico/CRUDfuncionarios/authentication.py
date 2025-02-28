from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)

        if result is None:
            raise AuthenticationFailed('Invalid credentials')

        user, token = result

        return (user, token)
