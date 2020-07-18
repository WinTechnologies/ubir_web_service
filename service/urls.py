from rest_framework.routers import SimpleRouter

from .views import ServiceViewSet

router = SimpleRouter()
router.register(r'service', ServiceViewSet, basename='service')
