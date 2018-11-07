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
    first_name = forms.CharField(max_length=40, required=True)
    last_name = forms.CharField(max_length=40, required=True)
    email = forms.EmailField(max_length=254, required=True)
    address = forms.CharField(max_length=254, required=True)
    state = USStateField(required=True, widget=USStateSelect())
    city = forms.CharField(max_length=85, required=True)
    zip_code = USZipCodeField(required=True)

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
        for character in first_name:
            if character in "!@#$%^&*()~,./?;:1234567890}{<>-+=":
                print('{field} contains {character}')
                raise forms.ValidationError('You included a number or special character in a name or city field')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        for character in last_name:
            if character in "!@#$%^&*()~,./?;:1234567890}{<>-+=":
                print('{field} contains {character}')
                raise forms.ValidationError('You included a number or special character in a name or city field')
        return last_name

    def clean_city(self):
        city = self.cleaned_data['city']
        for character in city:
            if character in "!@#$%^&*()~,./?;:1234567890}{<>-+=":
                print('{field} contains {character}')
                raise forms.ValidationError('You included a number or special character in a name or city field')
        return city


class ForgotPasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email == '':
            raise forms.ValidationError(_("Email cannot be blank.  Please supply an email address."))
        return email


class SecurityQuestionForm(forms.Form):
    security_answer = forms.CharField(required=True)

    class Meta:
        fields = ['security_answer']


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        fields = ['password', 'confirm_password']


class UpdateUserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ChangeUsernameForm(forms.ModelForm):
    username = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username']



class ValidatingPasswordChangeForm(auth.forms.PasswordChangeForm):
    min_length = 8

    def clean_new_password1(self):
        min_length = 8
        upper = False
        lower = False
        digit = False
        password = self.cleaned_data.get('new_password1')

        if len(password) < min_length:
            raise forms.ValidationError(_("Password must be at least 8 characters long."))

        for c in password:
            if c.isupper():
                upper = True
            if c.isalpha() and not c.isupper():
                lower = True
            if c.isdigit():
                digit = True

        if not (upper and lower and digit):
            raise forms.ValidationError(
                _("Password must contain at least one uppercase letter, one lowercase letter, and one digit."))

        return password