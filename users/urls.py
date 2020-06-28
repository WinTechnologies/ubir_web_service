from rest_framework.routers import SimpleRouter

from ubir_assist.users.views import UserCreateViewSet

router = SimpleRouter()
router.register(r'users', UserCreateViewSet)
