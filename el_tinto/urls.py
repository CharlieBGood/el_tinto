from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from el_tinto.web_page.views.index import index
from el_tinto.web_page.views.faqs import faqs
from el_tinto.web_page.views.suscribe import suscribe
from el_tinto.web_page.views.who_are_we import who_are_we
from el_tinto.web_page.views.unsuscribe import unsuscribe
from el_tinto.web_page.views.old_index import old_index
from el_tinto.web_page.views.customize import customize
from el_tinto.web_page.views.customize_days import customize_days

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', who_are_we, name='index'),
    path('suscribirse/', suscribe, name='suscribe'),
    path('desuscribirse/adios/', unsuscribe, name='unsuscribe'),
    path('el-tinto/', index, name='el_tinto'),
    path('el_tinto/', old_index, name='el_tinto_old'),
    path('faq/', faqs, name='faqs'),
    path('desuscribirse/personalizar/', customize, name='unsuscribe_customize'),
    path('personalizar/', customize, name='customize'),
    path('personalizar/dias/', customize_days, name='customize_days'),
    path('sns/', include('el_tinto.ses_sns.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'el_tinto.web_page.views.404_error.error_404_view'
handler500 = 'el_tinto.web_page.views.500_error.error_500_view'
