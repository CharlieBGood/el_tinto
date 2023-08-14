from django.urls import path

from el_tinto.users.views import RegisterView, UpdatePreferredDaysView, ConfirmUpdatePreferredDaysView, \
    UnsuscribeView, ReferralHubView, SendMilestoneMailView, UserVisitsView, UserButtonsInteractionsView

urlpatterns = [
    path('suscribe/', RegisterView.as_view(), name='register'),
    path('update_preferred_days/', UpdatePreferredDaysView.as_view()),
    path('update_preferred_days/confirm/', ConfirmUpdatePreferredDaysView.as_view()),
    path('unsuscribe/', UnsuscribeView.as_view()),
    path('referral_hub/', ReferralHubView.as_view()),
    path('send_milestone_mail/', SendMilestoneMailView.as_view()),
    path('user_visits/', UserVisitsView.as_view()),
    path('user_button_interaction/', UserButtonsInteractionsView.as_view()),
]

