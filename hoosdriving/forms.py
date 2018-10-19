from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm
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

class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=40, required=True, help_text='Required')
    last_name = forms.CharField(max_length=40, required=True, help_text='Required')
    email = forms.EmailField(max_length=254, required=True, help_text='Required')
    address = forms.CharField(max_length=254, required=True, help_text='Required')
    state = USStateField(required=True, widget=USStateSelect(), help_text='Required')
    city = forms.CharField(max_length=85, required=True, help_text='Required')
    zip_code = USZipCodeField(required=True, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name',
                  'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        return last_name

    def clean_city(self):
        city = self.cleaned_data['city']
        return city