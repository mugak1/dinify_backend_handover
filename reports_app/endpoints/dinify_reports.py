from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from reports_app.controllers.dinify.dashboard import generate_dinify_dashboard


class DinifyReportsEndpoint(APIView):
    def get(self, request, report_name):
        date_today = datetime.now().date()
        if report_name == 'dashboard':
            response = generate_dinify_dashboard()
        return Response(response)
