from django.urls import path
from api.views.organization import OrganizationApi, BranchApi, TableApi, TerminalApi, BlockAccountView
from rest_framework import routers

router = routers.DefaultRouter()

router.register("organization", OrganizationApi)
router.register("branch", BranchApi)
router.register("table", TableApi)
router.register("terminal", TerminalApi)


urlpatterns = [
    path("block-account/", BlockAccountView.as_view())
] + router.urls
