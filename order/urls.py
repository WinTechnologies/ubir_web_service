from rest_framework.routers import SimpleRouter

from .views import OrderViewSet

router = SimpleRouter()
router.register(r'order', OrderViewSet, basename='order')
