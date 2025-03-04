from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from purchase.models import Production
import json

@permission_classes([AllowAny])
@api_view(['POST'])
def create_bulk_production(request):
    data = request.data.get('data', None)
    if data:
        data = json.loads(data)
        for k,v in data.items():
            Production.objects.create(product_id=int(k), quantity = int(v))
    return Response({'message': 'ok'})