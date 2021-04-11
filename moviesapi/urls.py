from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include, re_path
from .yasg import urlpatterns as doc_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('movies.urls')),
    path('api/', include('accounts.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.urls.authtoken')),
    path('api-auth/', include('rest_framework.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # path('api/v1/profile', include('profiles.urls')),
    # path('api/v1/account', include('accounts.urls')),
]

urlpatterns += doc_urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
