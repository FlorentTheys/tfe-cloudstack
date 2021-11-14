from django import forms


class APIKeyForm(forms.Form):
    API_key = forms.CharField(label='Your API Key', max_length=100)
