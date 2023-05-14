from django.urls import path

from el_tinto.users.views import RegisterView, UpdatePreferredDaysView, ConfirmUpdatePreferredDaysView, \
    UnsuscribeView, ReferralHubView

urlpatterns = [
    path('suscribe/', RegisterView.as_view()),
    path('update_preferred_days/', UpdatePreferredDaysView.as_view()),
    path('update_preferred_days/confirm/', ConfirmUpdatePreferredDaysView.as_view()),
    path('unsuscribe/', UnsuscribeView.as_view()),
    path('referral_hub/', ReferralHubView.as_view())
]

