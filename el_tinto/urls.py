from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

router = DefaultRouter()

urlpatterns = [
    path('cafetera/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('api/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include('el_tinto.web_page.urls')),
    path('sns/', include('el_tinto.ses_sns.urls')),
    path('', include('el_tinto.tintos.urls')),
    path('', include('el_tinto.advertisement.urls')),
    path('mails/', include('el_tinto.mails.urls'))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'el_tinto.web_page.views.404_error.error_404_view'
handler500 = 'el_tinto.web_page.views.500_error.error_500_view'
