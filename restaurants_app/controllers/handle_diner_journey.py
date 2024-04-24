from restaurants_app.models import Table
from restaurants_app.serializers import SerializerPublicGetTableDetails
from dinify_backend.configss.messages import OK_SCANNED_TABLE


def handle_table_scan(table_id: str) -> dict:
    table = Table.objects.get(id=table_id)
    table_data = SerializerPublicGetTableDetails(
        table, many=False
    ).data
    return {
        'status': 200,
        'message': OK_SCANNED_TABLE,
        'data': table_data
    }

