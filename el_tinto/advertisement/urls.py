from django.urls import path

from el_tinto.advertisement.views import suscribe_lead

urlpatterns = [
    path('lead/<str:lead_type>', suscribe_lead, name='suscribe_lead'),
]
