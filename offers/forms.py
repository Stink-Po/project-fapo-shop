from django import forms
from django.utils import timezone
from .models import Offer


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['name', 'code', 'discount_amount', 'image', 'start_date', 'end_date', 'is_active']

    # Optionally, you can add custom validation here for certain fields if necessary.
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < timezone.now():
            raise forms.ValidationError("Start date cannot be in the past.")
        return start_date

    def clean_code(self):
        code = self.cleaned_data.get('code')
        list_code = code.split()
        persian_digits = {
            '۰': "0",
            "۱": "1",
            "۲": "2",
            "۳": "3",
            "۴": "4",
            "۵": "5",
            "۶": "6",
            "۷": "7",
            "۸": "8",
            "۹": "9",
        }
        final_code = ""
        for i in list_code:
            for key, value in persian_digits.items():
                if i == key:
                    final_code += value
            final_code += i

        return final_code

    def clean_image(self):
        image = self.cleaned_data.get('image')
        # Allow the image to be empty
        if not image:
            return None
        return image

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')
        if end_date and start_date and end_date <= start_date:
            raise forms.ValidationError("End date must be after the start date.")
        return end_date
