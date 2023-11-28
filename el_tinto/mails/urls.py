from django.urls import path
from rest_framework.routers import DefaultRouter

from el_tinto.mails.views import TemplatesViewSet, MailsViewset, MailLinkView

app_name = 'mails'

mails_router = DefaultRouter()

mails_router.register(r'templates', TemplatesViewSet, basename='templates')
mails_router.register(r'', MailsViewset, basename='mails')

urls = [
    path('redirect/<code>', MailLinkView.as_view(), name='link_redirect')
]

urlpatterns = mails_router.urls + urls
