from rest_framework.routers import SimpleRouter

from .views import UBIRWiFiViewSet

router = SimpleRouter()
router.register(r'customer', UBIRWiFiViewSet, basename='customer')
