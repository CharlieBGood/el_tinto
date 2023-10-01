from django.urls import path

from el_tinto.users.views import RegisterView, UpdatePreferredDaysView, ConfirmUpdatePreferredDaysView, \
    UnsuscribeView, ReferralHubView, SendMilestoneMailView, UserVisitsView, UserButtonsInteractionsView, \
    MyTasteClubView, MyTasteClubActionsView

urlpatterns = [
    path('suscribe/', RegisterView.as_view(), name='register'),
    path('update_preferred_days/', UpdatePreferredDaysView.as_view()),
    path('update_preferred_days/confirm/', ConfirmUpdatePreferredDaysView.as_view()),
    path('unsuscribe/', UnsuscribeView.as_view()),
    path('referral_hub/', ReferralHubView.as_view()),
    path('send_milestone_mail/', SendMilestoneMailView.as_view()),
    path('user_visits/', UserVisitsView.as_view()),
    path('user_button_interaction/', UserButtonsInteractionsView.as_view()),
    path('my_taste_club/<uuid>/', MyTasteClubView.as_view(), name='my_taste_club'),
    path('my_taste_club/<id>/<action>/', MyTasteClubActionsView.as_view(), name='my_taste_club_actions'),
]

