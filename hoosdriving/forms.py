from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from localflavor.us.forms import USZipCodeField, USStateSelect, USStateField

class LoginForm(forms.Form):
    username = forms.CharField(label='Username or email')
    password = forms.CharField(widget=forms.PasswordInput)

class ContactForm(forms.Form):
    contact_name = forms.CharField(required=True, label="Name")
    contact_email = forms.EmailField(required=True, label="Email")
    content = forms.CharField(
        required=True,
        widget=forms.Textarea,
        label="Message"
    )

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'confirm_password']

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        address = forms.CharField(max_length=254, required=True, help_text='Required')
        state = USStateField(required=True, widget=USStateSelect(), help_text='Required')
        city = forms.CharField(max_length=85, required=True, help_text='Required')
        zip_code = USZipCodeField(required=True, help_text='Required')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))

        if email == '':
            raise forms.ValidationError(_("Email cannot be blank.  Please supply an email address."))
        return email