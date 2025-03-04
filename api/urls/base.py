from .user import urlpatterns as user_urlpatterns
from .product import urlpatterns as product_urlpatterns
from .bill import urlpatterns as bill_urlpatterns
from .organization import urlpatterns as org_urlpatterns
from .discount_urls import urlpatterns as discount_urlspatterns
from .accounting_urls import urlpatterns as accounting_urlpatterns
from .purchase import urlpatterns as purchase_urlpatterns
from .delivery import urlpatterns as delivery_patterns

urlpatterns = (
    [] + user_urlpatterns + product_urlpatterns + bill_urlpatterns + org_urlpatterns+discount_urlspatterns+ accounting_urlpatterns + purchase_urlpatterns + delivery_patterns
)
