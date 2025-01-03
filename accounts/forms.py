from django import forms
import re
from cities.models import City, State
from .models import CustomUser

class GetPhoneNumberForm(forms.Form):
    phone = forms.CharField(
        max_length=11,
        label="شماره همراه خود را وارد کنید",
        widget=forms.TextInput(attrs={'placeholder': 'مثال 09128885544'})
    )

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_email"]
        if re.match(r'^\d{11}$', phone):
            return phone

        else:
            raise forms.ValidationError("شماره تلفن یا ایمیل وارد شده صحیح نمی باشد")



class ProfileForm(forms.Form):
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
        self.fields['province'].label = 'استان'
        self.fields['city'].label = 'شهر'
        self.fields['address'].label = 'آدرس'
        self.fields['zip_code'].label = 'کد پستی'
        self.fields["email"].label = 'پست الکترونیک'
        self.fields["phone"].label = "تلفن همراه"

        if 'province' in self.data:
            try:
                state_id = int(self.data.get('province'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_id).order_by('name')
                self.fields['city'].empty_label = 'شهر خود را انتخاب کنید'
            except (ValueError, TypeError):
                pass


    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("این پست الکترونیک قبلاً ثبت شده است.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Exclude the current user's phone number from the uniqueness check
            if CustomUser.objects.filter(phone_number=phone).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError("این شماره تلفن قبلاً ثبت شده است.")
        return phone


