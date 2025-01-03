from django import forms
from cities.models import City, State


class OrderAdressForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    province = forms.ModelChoiceField(queryset=State.objects.all(), empty_label="استان خود را انتخاب کنید")
    city = forms.ModelChoiceField(queryset=City.objects.none(), empty_label="شهر خود را انتخاب کنید")
    address = forms.CharField(widget=forms.Textarea)
    zip_code = forms.CharField(max_length=10)
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=11)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'نام'
        self.fields['last_name'].label = 'نام خانوادگی'
        self.fields["phone"].label = "تلفن همراه"
        self.fields['province'].label = 'استان'
        self.fields['city'].label = 'شهر'
        self.fields['address'].label = 'آدرس'
        self.fields['zip_code'].label = 'کد پستی'
        self.fields["email"].label = 'پست الکترونیک'

        if 'province' in self.data:
            try:
                state_id = int(self.data.get('province'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_id).order_by('name')
                self.fields['city'].empty_label = 'شهر خود را انتخاب کنید'
            except (ValueError, TypeError):
                pass