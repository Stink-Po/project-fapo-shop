from django import forms

class SearchForm(forms.Form):
    query = forms.CharField()


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 7,
        'placeholder': 'دیدگاه شما',
        'class': 'form-control',
        'id': 'commentbody',
        'required': 'required',
    }))

