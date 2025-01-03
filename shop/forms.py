from django import forms


class SortCategoriesForm(forms.Form):
    sort_value = forms.ChoiceField(
        choices=[
            ('default', 'پیش فرض'),
            ('favorite', 'محبوب ترین'),
            ('must_sell', 'پرفروش ترین'),
            ('cheaper', 'ارزان ترین'),
            ('expensive', 'گران ترین'),
            ('new', 'جدید ترین'),
        ],

    )
