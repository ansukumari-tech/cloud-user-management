from unittest.mock import patch

import jwt
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


def make_token(username, role):
    return jwt.encode({"sub": username, "role": role}, settings.JWT_SECRET_KEY, algorithm="HS256")


class AuthenticationTests(APITestCase):
    def test_no_token_is_rejected(self):
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_garbage_token_is_rejected(self):
        response = self.client.get(reverse("user-list"), HTTP_AUTHORIZATION="Bearer not-a-real-token")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_token_is_forbidden(self):
        token = make_token("bob", "user")
        response = self.client.get(reverse("user-list"), HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserListViewTests(APITestCase):
    @patch("users.views.client.list_users")
    def test_admin_token_triggers_call_to_auth_service(self, mock_list_users):
        mock_list_users.return_value = [{"id": 1, "username": "admin1", "role": "admin"}]
        token = make_token("admin1", "admin")

        response = self.client.get(reverse("user-list"), HTTP_AUTHORIZATION=f"Bearer {token}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [{"id": 1, "username": "admin1", "role": "admin"}])
        mock_list_users.assert_called_once()


class UserDetailViewTests(APITestCase):
    def setUp(self):
        self.token = make_token("admin1", "admin")
        self.auth_header = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

    @patch("users.views.client.update_user")
    def test_update_delegates_to_auth_service(self, mock_update):
        mock_update.return_value = {"id": 2, "username": "bob", "role": "admin"}

        response = self.client.put(reverse("user-detail", args=[2]), {"role": "admin"}, **self.auth_header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update.assert_called_once_with(2, username=None, role="admin")

    @patch("users.views.client.delete_user")
    def test_delete_delegates_to_auth_service(self, mock_delete):
        mock_delete.return_value = {"msg": "User deleted successfully"}

        response = self.client.delete(reverse("user-detail", args=[2]), **self.auth_header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_delete.assert_called_once_with(2)
