from django import forms


class TicketsForm(forms.Form):
    title = forms.CharField(label='عنوان')
    description = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'پیام خوذ را وارد کنید ...'}))


class TicketResponseForm(forms.Form):
    response = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'پیام خوذ را وارد کنید ...'}))