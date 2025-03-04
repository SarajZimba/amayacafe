from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
"""
Standard Group names

admin
agent
Accounting
Store Keeper

"""

class CheckPermissionMixin(object):
    perm_group = [
        "admin",
    ]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name__in=self.perm_group).exists():
                return super().dispatch(request, *args, **kwargs)
        return redirect(reverse_lazy("user:login_view"))

class SearchMixin:
    search_lookup_fields = []
    valid_date_filter = ["created_at", "-created_at", "updated_at", "-updated_at"]

    def get_queryset(self, *args, **kwargs):
        qc = super().get_queryset(*args, **kwargs)
        qc = self.search(qc)
        qc = self.date_filter(qc)
        qc = self.date_range_filter(qc)
        return qc

    def date_filter(self, qc):
        if self.request.GET.get("sort_date"):
            sort_date = self.request.GET.get("sort_date")
            if sort_date in self.valid_date_filter:
                return qc.order_by(sort_date)
        return qc

    def date_range_filter(self, qc):
        
        if self.request.GET.get("fromDate") and self.request.GET.get("toDate"):
            created_at_date = self.request.GET.get("fromDate")
            created_to_date = self.request.GET.get("toDate")
            print(qc.filter(created_at__range=[created_at_date, created_to_date]))
            return qc.filter(created_at__range=[created_at_date, created_to_date])
        return qc

    def search(self, qc):
        if self.request.GET.get("q"):
            query = self.request.GET.get("q")
            q_lookup = Q()
            for field in self.search_lookup_fields:
                q_lookup |= Q(**{field + "__icontains": query})
            return qc.filter(q_lookup)
        return qc


class BillFilterMixin:
    search_lookup_fields = [
        # "customer_name",
        # "miti",
        # "bill_no",
        # "customer_pan",
        "customer_name",
        "invoice_number",
        "customer_tax_number",
        "terminal",
    ]

    def get_queryset(self, *args, **kwargs):
        qc = super().get_queryset(*args, **kwargs)
        qc = self.search(qc)
        return qc

    def search(self, qc):
        if self.request.GET.get("q"):
            query = self.request.GET.get("q")
            q_lookup = Q()
            for field in self.search_lookup_fields:
                q_lookup |= Q(**{field + "__icontains": query})
            return qc.filter(q_lookup)
        return qc


# this checks if the user is in group Admin or not
class IsAdminMixin(SearchMixin, object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name="admin").exists():
                return super().dispatch(request, *args, **kwargs)
        return redirect(reverse_lazy("user:login_view"))


class IsAccountantMixin(BillFilterMixin, object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name="admin").exists():
                return super().dispatch(request, *args, **kwargs)
        return redirect(reverse_lazy("user:login_view"))


class IsAdminOrAccountingMixin(SearchMixin):
    perm_group = [
        "admin",
        "Accounting"
    ]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name__in=self.perm_group).exists():
                return super().dispatch(request, *args, **kwargs)
        return redirect(reverse_lazy("user:login_view"))
    
class IsAdminAccountingOrStoreKeeperMixin(SearchMixin):
    perm_group = [
        "admin",
        "Accounting",
        "Store Keeper"
    ]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name__in=self.perm_group).exists():
                return super().dispatch(request, *args, **kwargs)
        return redirect(reverse_lazy("user:login_view"))

