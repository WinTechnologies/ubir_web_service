from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls import url
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter

from customer.urls import router as customer_router
# from ubir_assist.users.views import MyTokenObtainPairView, MyTokenRefreshView, MyTokenVerifyView
from rest_framework_swagger.views import get_swagger_view

router = DefaultRouter()
router.registry.extend(customer_router.registry)

schema_view = get_swagger_view(title="Swagger Docs")

urlpatterns = [
    url(r'^swagger/', schema_view),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    # path('api/v1/', include(router.urls)),
    # path('api/v1/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/v1/token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    # path('api/v1/token/verify/', MyTokenVerifyView.as_view(), name='token_verify'),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    # re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
