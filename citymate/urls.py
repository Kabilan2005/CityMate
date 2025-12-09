from django.contrib import admin
from django.urls import path, include
from users.views import WelcomeView
from django.conf import settings               
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', WelcomeView.as_view(), name='welcome'),
    path('', include(('users.urls', 'users'), namespace='users')),
    path('places/', include(('places.urls', 'places'), namespace='places')),
    
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()