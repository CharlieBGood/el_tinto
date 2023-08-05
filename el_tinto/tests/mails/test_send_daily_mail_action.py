from django.test import TestCase
from django.shortcuts import reverse
from el_tinto.tests.mails.factories import DailyMailFactory
from el_tinto.tests.users.factories import EditorFactory


class SendDailyMailAction(TestCase):

    def setUp(self):
        self.daily_mail = DailyMailFactory()
        self.data = {'action': 'send_daily_mail', '_selected_action': [self.daily_mail.id]}
        self.url = reverse('admin:mails_mail_changelist')

        self.editor = EditorFactory()
        self.client.force_login(self.editor)

