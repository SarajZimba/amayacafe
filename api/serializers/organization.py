from importlib.metadata import MetadataPathFinder
from rest_framework.serializers import ModelSerializer
from organization.models import Branch, Organization, Table, Terminal, PrinterSetting
from rest_framework import serializers

class BlockAccountSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=7)
    blocked = serializers.CharField(max_length=4)
    key = serializers.CharField(max_length=255)
    device_id = serializers.CharField(max_length=100, required=False)


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "org_name",
            "org_logo",
            "tax_number",
            "website",
            "company_contact_number",
            "company_contact_email",
            "contact_person_number",
            "company_address",
            "company_bank_qr",
            "current_fiscal_year"
        ]

class TableSerializer(ModelSerializer):
    class Meta:
        model = Table
        fields = 'table_number', 'is_occupied'
    
    def to_representation(self, instance):
        return super().to_representation(instance)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_deleted=False)


class PrinterSettingSerializer(ModelSerializer):
    
    type = serializers.SerializerMethodField()

    class Meta:
        model = PrinterSetting
        fields = "url", "port", "ip", "type"
    
    def get_type(self, obj):
        return obj.printer_location


class TerminalSerialzier(ModelSerializer):
    # tables = TableSerializer(many=True, read_only=True, source="table_set")
    tables = serializers.SerializerMethodField()
    printers = PrinterSettingSerializer(many=True, read_only=True, source="printersetting_set")
    class Meta:
        model = Terminal
        fields = "id", "terminal_no", "tables", "printers",
        
    # def get_active_tables(self, obj):
    #     return obj.table_set.filter(is_deleted=False)
    
    def get_tables(self, obj):
        active_tables = obj.table_set.filter(is_deleted=False)
        serializer = TableSerializer(instance=active_tables, many=True)
        return serializer.data
        

class BranchSerializer(ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "address",
            "contact_number",
            "branch_manager",
            "organization",
            "branch_code",
        ]
