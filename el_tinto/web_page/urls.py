from django.urls import path
from el_tinto.web_page.views.index import index
from el_tinto.web_page.views.faqs import faqs
from el_tinto.web_page.views.referral_hub import referral_hub
from el_tinto.web_page.views.suscribe import suscribe
from el_tinto.web_page.views.who_are_we import who_are_we
from el_tinto.web_page.views.unsuscribe import unsuscribe
from el_tinto.web_page.views.old_index import old_index
from el_tinto.web_page.views.customize import customize
from el_tinto.web_page.views.customize_days import customize_days
from el_tinto.web_page.views.news import news

urlpatterns = [
    path('', who_are_we, name='index'),
    path('suscribirse/', suscribe, name='suscribe'),
    path('desuscribirse/adios/', unsuscribe, name='unsuscribe'),
    path('el-tinto-de-hoy/', index, name='el_tinto'),
    path('el_tinto/', old_index, name='el_tinto_old'),
    path('faq/', faqs, name='faqs'),
    path('desuscribirse/personalizar/', customize, name='unsuscribe_customize'),
    path('personalizar/', customize, name='customize'),
    path('personalizar/dias/', customize_days, name='customize_days'),
    path('noticias/<int:news_id>/', news, name='news'),
    path('referidos/', referral_hub, name='referral_hub'),
]
