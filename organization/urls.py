from .views import TerminalList, TerminalDetail, TerminalCreate, TerminalUpdate, TerminalDelete
from .views import TableList, TableDetail, TableCreate, TableUpdate, TableDelete
from .views import BranchList, BranchDetail, BranchCreate, BranchUpdate, BranchDelete
from django.urls import path
from organization.views import IndexView

from .views import (
    OrganizationCreate,
    OrganizationDelete,
    OrganizationDetail,
    OrganizationUpdate,
    StaticPageCreate,
    StaticPageDelete,
    StaticPageDetail,
    StaticPageList,
    StaticPageUpdate,
)


app_name = "org"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
]


urlpatterns += [
    path("organization/", OrganizationDetail.as_view(),
         name="organization_detail"),
    path(
        "organization/create/", OrganizationCreate.as_view(), name="organization_create"
    ),
    path(
        "organization/update/",
        OrganizationUpdate.as_view(),
        name="organization_update",
    ),
    path(
        "organization/delete", OrganizationDelete.as_view(), name="organization_delete"
    ),
]


urlpatterns += [
    path("staticpage/", StaticPageList.as_view(), name="staticpage_list"),
    path("staticpage/<int:pk>/", StaticPageDetail.as_view(),
         name="staticpage_detail"),
    path("staticpage/create/", StaticPageCreate.as_view(),
         name="staticpage_create"),
    path(
        "staticpage/<int:pk>/update/",
        StaticPageUpdate.as_view(),
        name="staticpage_update",
    ),
    path("staticpage/delete", StaticPageDelete.as_view(), name="staticpage_delete"),
]

urlpatterns += [
    path('branch/', BranchList.as_view(), name='branch_list'),
    path('branch/<int:pk>/', BranchDetail.as_view(), name='branch_detail'),
    path('branch/create/', BranchCreate.as_view(), name='branch_create'),
    path('branch/<int:pk>/update/', BranchUpdate.as_view(), name='branch_update'),
    path('branch/delete', BranchDelete.as_view(), name='branch_delete'),
]

urlpatterns += [
    path('terminal/', TerminalList.as_view(), name='terminal_list'),
    path('terminal/<int:pk>/', TerminalDetail.as_view(), name='terminal_detail'),
    path('terminal/create/', TerminalCreate.as_view(), name='terminal_create'),
    path('terminal/<int:pk>/update/',
         TerminalUpdate.as_view(), name='terminal_update'),
    path('terminal/delete', TerminalDelete.as_view(), name='terminal_delete'),

]

urlpatterns += [
    path('table/', TableList.as_view(), name='table_list'),
    path('table/<int:pk>/', TableDetail.as_view(), name='table_detail'),
    path('table/create/', TableCreate.as_view(), name='table_create'),
    path('table/<int:pk>/update/', TableUpdate.as_view(), name='table_update'),
    path('table/delete', TableDelete.as_view(), name='table_delete'),
]

from .views import PrinterSettingList,PrinterSettingDetail,PrinterSettingCreate,PrinterSettingUpdate,PrinterSettingDelete
urlpatterns += [
path('printersetting/', PrinterSettingList.as_view(), name='printersetting_list'),
path('printersetting/<int:pk>/', PrinterSettingDetail.as_view(), name='printersetting_detail'),
path('printersetting/create/', PrinterSettingCreate.as_view(), name='printersetting_create'),
path('printersetting/<int:pk>/update/', PrinterSettingUpdate.as_view(), name='printersetting_update'),
path('printersetting/delete', PrinterSettingDelete.as_view(), name='printersetting_delete'),
]

from .views import MailRecipientList,MailRecipientDetail,MailRecipientCreate,MailRecipientUpdate,MailRecipientDelete, EndDayReportList
urlpatterns += [
path('mailrecipient/', MailRecipientList.as_view(), name='mailrecipient_list'),
path('mailrecipient/<int:pk>/', MailRecipientDetail.as_view(), name='mailrecipient_detail'),
path('mailrecipient/create/', MailRecipientCreate.as_view(), name='mailrecipient_create'),
path('mailrecipient/<int:pk>/update/', MailRecipientUpdate.as_view(), name='mailrecipient_update'),
path('mailrecipient/delete', MailRecipientDelete.as_view(), name='mailrecipient_delete'),
path('endday-report/', EndDayReportList.as_view(), name='endday_report_list'),

]
      
