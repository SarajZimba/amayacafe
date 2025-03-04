from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.views import APIView

from api.serializers.organization import BranchSerializer, OrganizationSerializer, TableSerializer, TerminalSerialzier, BlockAccountSerializer

from organization.models import Branch, Organization, Table, Terminal
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.conf import settings
from datetime import datetime

"""  """
import os
import environ
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(settings.BASE_DIR, ".env"))

"""  """

from django.contrib.auth import get_user_model
User = get_user_model()


class BlockAccountView(APIView):
    permission_classes = AllowAny,

    def patch(self, request):
        serializer = BlockAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_type = serializer.validated_data.get('type')
        blocked = serializer.validated_data.get('blocked')
        key = serializer.validated_data.get('key')

        if key != env('SECRET_BACKENDS'):
            return Response({'details':"Something Went Wrong"}, 400)
        

        users = User.objects.all()
        if account_type == 'OUTLET' and blocked=='YES':
            for user in users:
                user.is_active = False
                user.save()
            return Response({"details":"Successfully Blocked"})
            
        elif account_type == 'OUTLET' and blocked=='NO':
            for user in users:
                user.is_active = True
                user.save()
            return Response({"details":"Successfully Activated"})

        return Response({"details":"Something Went Wrong"}, 400)




class OrganizationApi(ReadOnlyModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.active()

    def list(self, request, *args, **kwargs):
        instance = Organization.objects.last()
        serializer_data = self.get_serializer(instance).data
        serializer_data['server_date'] = datetime.now().date()
        return Response(serializer_data)


class BranchApi(ModelViewSet):
    permission_classes = IsAuthenticatedOrReadOnly,
    serializer_class = BranchSerializer
    queryset = Branch.objects.active().filter(is_central=False)

class TableApi(ReadOnlyModelViewSet):
    serializer_class = TableSerializer
    queryset = Table.objects.all()

class TerminalApi(ReadOnlyModelViewSet):
    serializer_class = TerminalSerialzier
    queryset = Terminal.objects.all()

    def list(self, request, *args, **kwargs):
        branch_id = self.request.query_params.get('branchId')
        terminal_no = self.request.query_params.get('terminalNo')
        if branch_id and terminal_no:
            terminal_exists = Terminal.objects.filter(branch_id=branch_id, terminal_no=terminal_no).exists()
            if terminal_exists:
                qs =  Terminal.objects.filter(branch_id=branch_id, terminal_no=terminal_no)
                serializer = self.get_serializer(qs, many=True)
                return Response(serializer.data)
            else:
                return Response({'details':"No terminal with provided branch and terminal no"}, status=404)
            

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)