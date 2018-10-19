from django.contrib.auth import authenticate, login
from .forms import *
from django import forms
from django.contrib.auth.models import User
from django.views.generic import View
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib.auth.password_validation import password_validators_help_texts, validate_password, get_password_validators
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .settings import AUTH_PASSWORD_VALIDATORS

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_name = form.cleaned_data['contact_name']
            contact_email = form.cleaned_data['contact_email']
            content = form.cleaned_data['content']
            email = EmailMessage(contact_name, content, contact_email, ['djm3am@virginia.edu'], reply_to=[contact_email])
            email.send()
            return redirect('')
    return render(request, 'contact.html', {'form': form})

class LoginFormView(View):
    form_class = LoginForm
    template_name = 'loginform.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                email_login = User.objects.filter(email=username).first()
                if email_login is not None:
                    username = email_login.username
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect('/')

                form.add_error('password', forms.ValidationError(_("Invalid login.")))

        return render(request, self.template_name, {'form': form})


def SignupFormView(request):
    template_name = 'signupform.html'

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save();
            user.refresh_from_db()
            user.profile.address = form.cleaned_data.get('address')
            user.profile.city = form.cleaned_data.get('city')
            user.profile.state = form.cleaned_data.get('state')
            user.profile.zip = form.cleaned_data.get('zip')
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/success.html')
    else:
        form = SignupForm()
    return render(request, template_name, {'form': form})