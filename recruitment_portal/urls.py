from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'jobs.views.custom_400_view'
handler403 = 'jobs.views.custom_403_view'
handler404 = 'jobs.views.custom_404_view'
handler500 = 'jobs.views.custom_500_view'
