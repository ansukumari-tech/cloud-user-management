import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class RemoteUser:
    """
    A lightweight stand-in for a Django user, built entirely from the JWT
    claims issued by auth-service. admin-service never queries a users
    table — it trusts the signature on the token instead.
    """

    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role
        self.is_authenticated = True

    def __str__(self):
        return self.username


class RemoteJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None

        token = header.split(" ", 1)[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        username = payload.get("sub")
        role = payload.get("role", "user")
        if not username:
            raise AuthenticationFailed("Token missing subject claim")

        return (RemoteUser(username=username, role=role), None)

    def authenticate_header(self, request):
        # Presence of this method tells DRF to return 401 (not 403) when no
        # valid token is supplied at all — 403 is reserved for "authenticated
        # but not permitted" (e.g. a non-admin token hitting an admin route).
        return "Bearer"
