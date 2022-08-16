from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .web_page.views import index, faqs, suscribe, who_are_we, unsuscribe, old_index, customize, customize_days

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', who_are_we, name='index'),
    path('suscribirse/', suscribe, name='suscribe'),
    path('desuscribirse/', unsuscribe, name='unsuscribe'),
    path('el-tinto/', index, name='el_tinto'),
    path('el_tinto/', old_index, name='el_tinto_old'),
    path('faq/', faqs, name='faqs'),
    path('personalizar/', customize, name='customize'),
    path('personalizar/dias/', customize, name='customize'),
    path('sns/', include('el_tinto.ses_sns.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'el_tinto.web_page.views.error_404_view'
handler500 = 'el_tinto.web_page.views.error_500_view'
