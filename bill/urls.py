from django.urls import path

urlpatterns = []

from .views import (
    BillList,
    BillDetail,
    BillCreate,
    BillUpdate,
    BillDelete,
    MaterializedView,
    MaterializedViewExportExcel,
    SalesEntryViewExportExcel,
    ReturnEntryViewExportExcel,
    IncrementBillPrintCount,
    MarkBillVoid,
    CustomerWiseSalesInvoiceRegister,
    PartyWiseSalesInvoiceRegister,
    SalesInvoiceSummaryRegister,
    SalesInvoiceAnalysis,
    PaymentModeSummary,
    TypeWiseSale,
    DeliveryList,
    DeliveryDetail,
    DeliveryCreate, 
    DeliveryDelete, 
    DeliveryUpdate
)

urlpatterns += [
    path("bill/", BillList.as_view(), name="bill_list"),
    path(
        "invoice-summary-register",
        SalesInvoiceSummaryRegister.as_view(),
        name="invoice_summary_register",
    ),
    path("bill/<int:pk>/", BillDetail.as_view(), name="bill_detail"),
    path("bill/create/", BillCreate.as_view(), name="bill_create"),
    path("bill/<int:pk>/update/", BillUpdate.as_view(), name="bill_update"),
    path("bill/delete", BillDelete.as_view(), name="bill_delete"),
    path("salebook/view/", MaterializedView.as_view(), name="materialized_view"),
    path(
        "bill/print/count/increment/",
        IncrementBillPrintCount.as_view(),
        name="increment_bill_print_count",
    ),
    path("bill/void/<int:id>", MarkBillVoid.as_view(), name="mark_bill_void"),
    path(
        "materialized/export/",
        MaterializedViewExportExcel.as_view(),
        name="materialized_export",
    ),
    # path(
    #     "sales/export/",
    #     SalesEntryViewExportExcel.as_view(),
    #     name="sales_export",
    # ),
    path(
        "cws/",
        CustomerWiseSalesInvoiceRegister.as_view(),
        name="customer_wise_sales",
    ),
    path(
        "pws/",
        PartyWiseSalesInvoiceRegister.as_view(),
        name="party_wise_sales",
    ),
    path("sia/", SalesInvoiceAnalysis.as_view(), name="sales_invoice_analysis"),
    path("pms/", PaymentModeSummary.as_view(), name="payment_mode_summary"),
    path("tws/", TypeWiseSale.as_view(), name="type_wise_sale"),
    # path(
    #     "returns/export/",
    #     ReturnEntryViewExportExcel.as_view(),
    #     name="returns_export",
    # ),
    path("delivery/", DeliveryList.as_view(), name="delivery_list"),
    path("delivery/<int:pk>/", DeliveryDetail.as_view(), name="delivery_detail"),
    path("delivery/create/", DeliveryCreate.as_view(), name="delivery_create"),
    path("delivery/<int:pk>/update/", DeliveryUpdate.as_view(), name="delivery_update"),
    path("delivery/delete", DeliveryDelete.as_view(), name="delivery_delete"),
]

from .views import (
    TblTaxEntryList,
    TblTaxEntryDetail,
    TblTaxEntryCreate,
    TblTaxEntryUpdate,
    TblTaxEntryDelete,
)

urlpatterns += [
    path("tbltaxentry/", TblTaxEntryList.as_view(), name="tbltaxentry_list"),
    path(
        "tbltaxentry/<int:pk>/", TblTaxEntryDetail.as_view(), name="tbltaxentry_detail"
    ),
    path("tbltaxentry/create/", TblTaxEntryCreate.as_view(), name="tbltaxentry_create"),
    path(
        "tbltaxentry/<int:pk>/update/",
        TblTaxEntryUpdate.as_view(),
        name="tbltaxentry_update",
    ),
    path("tbltaxentry/delete", TblTaxEntryDelete.as_view(), name="tbltaxentry_delete"),
]

from .views import (
    TblSalesEntryList,
    TblSalesEntryDetail,
    TblSalesEntryCreate,
    TblSalesEntryUpdate,
    TblSalesEntryDelete,
)

urlpatterns += [
    path("tblsalesentry/", TblSalesEntryList.as_view(), name="tblsalesentry_list"),
    path(
        "tblsalesentry/<int:pk>/",
        TblSalesEntryDetail.as_view(),
        name="tblsalesentry_detail",
    ),
    path(
        "tblsalesentry/create/",
        TblSalesEntryCreate.as_view(),
        name="tblsalesentry_create",
    ),
    path(
        "tblsalesentry/<int:pk>/update/",
        TblSalesEntryUpdate.as_view(),
        name="tblsalesentry_update",
    ),
    path(
        "tblsalesentry/delete",
        TblSalesEntryDelete.as_view(),
        name="tblsalesentry_delete",
    ),
]

from .views import (
    TablReturnEntryList,
    TablReturnEntryDetail,
    TablReturnEntryCreate,
    TablReturnEntryUpdate,
    TablReturnEntryDelete,
    TodaysTransactionView
)

urlpatterns += [
    path(
        "tablreturnentry/", TablReturnEntryList.as_view(), name="tablreturnentry_list"
    ),
    path(
        "tablreturnentry/<int:pk>/",
        TablReturnEntryDetail.as_view(),
        name="tablreturnentry_detail",
    ),
    path(
        "tablreturnentry/create/",
        TablReturnEntryCreate.as_view(),
        name="tablreturnentry_create",
    ),
    path(
        "tablreturnentry/<int:pk>/update/",
        TablReturnEntryUpdate.as_view(),
        name="tablreturnentry_update",
    ),
    path(
        "tablreturnentry/delete",
        TablReturnEntryDelete.as_view(),
        name="tablreturnentry_delete",
    ),
    path(
        "todays-transaction/",
        TodaysTransactionView.as_view(),
        name="todays_transaction",
    ),
]
