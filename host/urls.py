from rest_framework.routers import SimpleRouter

from .views import HostViewSet

router = SimpleRouter()
router.register(r'host', HostViewSet, basename='host')
