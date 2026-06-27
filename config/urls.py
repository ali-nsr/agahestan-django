from django.contrib import admin
from django.urls import path, include
from django.conf import settings as conf_settings

urlpatterns = [
    path('ad/', include('ad.urls', namespace='ad')),
    path('location/', include('location.urls', namespace='location')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('account/', include('accounts.urls', namespace='accounts')),
    path('social/', include('social.urls', namespace='social')),

    path('admin/', admin.site.urls),
]

if conf_settings.DEBUG:
    from django.conf.urls.static import static
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += static(conf_settings.STATIC_URL, document_root=conf_settings.STATIC_ROOT)
    urlpatterns += static(conf_settings.MEDIA_URL, document_root=conf_settings.MEDIA_ROOT)
    urlpatterns += debug_toolbar_urls()

# drf document
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Site API",
        default_version='v1',
        description="Site API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="ali92nsr@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
    # swagger
    path('swagger/output.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
