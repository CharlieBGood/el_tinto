from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .users.views import UserViewSet, UserCreateViewSet
from .web_page.views import index, faqs, suscribe, who_are_we, unsuscribe

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', index, name='index'),
    path('suscribirse/', suscribe, name='suscribe'),
    path('desuscribirse/', unsuscribe, name='unsuscribe'),
    path('quienes_somos/', who_are_we, name='who_are_we'),
    path('faq/', faqs, name='faqs'),
    path('sns/', include('el_tinto.ses_sns.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
