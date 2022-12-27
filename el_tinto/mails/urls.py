from rest_framework.routers import DefaultRouter

from el_tinto.mails.views import TemplatesViewSet, MailsViewset

mails_router = DefaultRouter()

mails_router.register(r'templates', TemplatesViewSet, basename='templates')
mails_router.register(r'', MailsViewset, basename='mails')

urlpatterns = mails_router.urls
