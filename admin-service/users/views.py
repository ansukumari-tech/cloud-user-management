from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAdminRole
from .services import AuthServiceClient, AuthServiceError

client = AuthServiceClient()


class UserListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        try:
            users = client.list_users()
        except AuthServiceError as exc:
            return Response({"msg": str(exc)}, status=exc.status_code)
        return Response(users, status=200)


class UserDetailView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        data = request.data
        if not data:
            return Response({"msg": "No data provided"}, status=400)
        try:
            updated = client.update_user(pk, username=data.get("username"), role=data.get("role"))
        except AuthServiceError as exc:
            return Response({"msg": str(exc)}, status=exc.status_code)
        return Response({"msg": "User updated successfully", "user": updated}, status=200)

    def delete(self, request, pk):
        try:
            client.delete_user(pk)
        except AuthServiceError as exc:
            return Response({"msg": str(exc)}, status=exc.status_code)
        return Response({"msg": "User deleted successfully"}, status=200)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "admin-service"}, status=200)
