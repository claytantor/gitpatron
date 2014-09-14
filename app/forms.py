from django import forms

class SettingsProfileForm(forms.Form):
    gravatar_email = forms.EmailField(
       label='Gravatar Email Address',
       max_length=64,
       required=False)

    # auto_merge = forms.BooleanField(label='Auto Merge on Fix Payment')
    #
    # auto_close = forms.BooleanField(label='Auto Close on Fix Payment')
