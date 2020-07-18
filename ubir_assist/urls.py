from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include, reverse_lazy
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from users.views import CustomAuthToken
from customer.views import CustomVerificationViewSet
from customer.urls import router as customer_router
from store.urls import router as store_router
from order.urls import router as order_router
from service.urls import router as service_router

router = DefaultRouter()
router.registry.extend(customer_router.registry)
router.registry.extend(store_router.registry)
router.registry.extend(order_router.registry)
router.registry.extend(service_router.registry)
router.register('phone', CustomVerificationViewSet, basename='phone')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/api-token-auth/', CustomAuthToken.as_view()),
    # path('api/v1/', include(router.urls)),
    # path('api/v1/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/v1/token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    # path('api/v1/token/verify/', MyTokenVerifyView.as_view(), name='token_verify'),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    # re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
