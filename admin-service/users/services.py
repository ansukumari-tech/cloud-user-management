"""
AuthServiceClient is the only thing in admin-service that knows how to
talk to auth-service. Views never construct requests themselves — this
keeps the HTTP/service-integration concern in one place (OOP + modular
design), and means swapping the transport (e.g. to gRPC later) only
touches this file.
"""
import requests
from django.conf import settings


class AuthServiceError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


class AuthServiceClient:
    def __init__(self, base_url: str = None, internal_key: str = None, timeout: float = 5.0):
        self.base_url = (base_url or settings.AUTH_SERVICE_URL).rstrip("/")
        self.internal_key = internal_key or settings.INTERNAL_SERVICE_KEY
        self.timeout = timeout

    def _headers(self):
        return {"X-Internal-Key": self.internal_key}

    def list_users(self):
        try:
            response = requests.get(
                f"{self.base_url}/internal/users", headers=self._headers(), timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise AuthServiceError(f"auth-service unreachable: {exc}") from exc

        if response.status_code != 200:
            raise AuthServiceError("Failed to fetch users from auth-service", response.status_code)
        return response.json()

    def update_user(self, user_id: int, username: str = None, role: str = None):
        payload = {k: v for k, v in {"username": username, "role": role}.items() if v is not None}
        try:
            response = requests.put(
                f"{self.base_url}/internal/users/{user_id}",
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise AuthServiceError(f"auth-service unreachable: {exc}") from exc

        if response.status_code == 404:
            raise AuthServiceError("User not found", 404)
        if response.status_code != 200:
            raise AuthServiceError("Failed to update user", response.status_code)
        return response.json()

    def delete_user(self, user_id: int):
        try:
            response = requests.delete(
                f"{self.base_url}/internal/users/{user_id}", headers=self._headers(), timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise AuthServiceError(f"auth-service unreachable: {exc}") from exc

        if response.status_code == 404:
            raise AuthServiceError("User not found", 404)
        if response.status_code != 200:
            raise AuthServiceError("Failed to delete user", response.status_code)
        return response.json()
