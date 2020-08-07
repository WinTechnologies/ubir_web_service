from rest_framework.routers import SimpleRouter

from .views import LogViewSet

router = SimpleRouter()
router.register(r'log', LogViewSet, basename='log')
