from django import forms
from el_tinto.users.models import Unsuscribe


class UserForm(forms.Form):
    
    email = forms.CharField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)


class UnsuscribeForm(forms.ModelForm):
    
    email = forms.CharField()
    
    class Meta:
        model = Unsuscribe
        fields = ('email', 'boring', 'invasive', 'variety', 'not_used', 'other_email', 'recommendation')
