from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection
from django.utils import timezone


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        # Check database connectivity
        db_ok = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_ok = True
        except Exception:
            pass

        return Response({
            'status': 'ok' if db_ok else 'degraded',
            'database': 'connected' if db_ok else 'unreachable',
            'timestamp': timezone.now().isoformat(),
        })
