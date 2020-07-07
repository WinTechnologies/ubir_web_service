from rest_framework.routers import SimpleRouter

from .views import StoreViewSet

router = SimpleRouter()
router.register(r'store', StoreViewSet, basename='store')
