from django.contrib.auth import authenticate, login
from .forms import *
from django import forms
from django.contrib.auth.models import User
from django.views.generic import View
from django.core.mail import EmailMessage
from .models import *
from .forms import *
from django import forms
from django.conf import settings
from django.views.generic import View
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import password_validators_help_texts, validate_password, get_password_validators
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from django.conf import settings
from .bitpay import Bitpay

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
            user = form.save()
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


def reset_password(request):
    form_class = ResetPasswordForm
    template_name = 'reset_password_form.html'

    if request.method == 'GET':
        form = form_class(None)
        return render(request, template_name, {'form': form})

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            validators = get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
            flag = 0
            for v in validators:
                try:
                    validate_password(password, password_validators=[v])
                except forms.ValidationError:
                    flag = 1
                    form.add_error('password',
                                   forms.ValidationError(_(password_validators_help_texts(password_validators=[v])[0])))

            if flag == 1:
                return render(request, template_name, {'form': form})

            if password != confirm_password:
                form.add_error('confirm_password',
                               forms.ValidationError(_("Passwords do not match.  Please try again.")))
                return render(request, template_name, {'form': form})

            user = User.objects.get(email=request.session.get('email', None))
            is_old_password = authenticate(username=user.username, password=password)
            if is_old_password is not None:
                form.add_error('confirm_password',
                               forms.ValidationError(_("New password cannot be the same as current password.")))
                return render(request, template_name, {'form': form})

            prof = Profile.objects.get(user=user)
            user.set_password(password)
            user.save()
            prof.user = user
            prof.save()
            return redirect('confirm_password_reset')

        return render(request, template_name, {'form': form})


def confirm_password_reset(request):
    return render(request, 'confirm_password_reset.html')


class UserProfileView(View):
    model = Profile

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        prof = Profile.objects.get(user=user)

        user_info = [("First name: ", user.first_name), ("Last name: ", user.last_name),
                         ("Username: ", user.username), ("Email: ", user.email)]
        return render(request, 'user_profile.html', {'user_info': user_info, 'user': user})



class UpdateUserProfileFormView(View):
    form_class = UpdateUserProfileForm
    template_name = 'update_user_info_form.html'

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        prof = Profile.objects.get(user=user)
        form = self.form_class(initial={'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email})
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, pk=pk)
            prof = Profile.objects.get(user=user)
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']

            if user.email != email and User.objects.filter(email=email).first() is not None:
                form.add_error('email', forms.ValidationError(_("This email address is already in use.")))
                return render(request, self.template_name, {'form': form})

            if user.first_name != first_name:
                user.first_name = first_name
            if user.last_name != last_name:
                user.last_name = last_name
            if user.email != email:
                user.email = email
            user.save()  # Update user information

            return HttpResponseRedirect(reverse('user_profile', args=(pk,)))

        return render(request, self.template_name, {'form': form})


@login_required
def change_username(request, pk):
    form_class = ChangeUsernameForm
    template_name = 'change_username_form.html'

    if request.method == 'GET':
        user = get_object_or_404(User, pk=pk)
        if not request.user.is_superuser:
            if request.user != user:
                return redirect('/')
        form = form_class(None)
        return render(request, template_name, {'form': form})

    if request.method == 'POST':
        form = form_class(request.POST)
        user = get_object_or_404(User, pk=pk)
        if form.is_valid():
            username = form.cleaned_data['username']
            prof = Profile.objects.get(user=user)
            user.username = username
            user.save()
            return HttpResponseRedirect(reverse('user_profile', args=(pk,)))

        return render(request, template_name, {'form': form})


@login_required
def change_password(request, pk):
    form_class = PasswordChangeForm
    template_name = 'change_password_form.html'

    if request.method == 'GET':
        form = form_class(request.user)
        user = get_object_or_404(User, pk=pk)
        if not request.user.is_superuser:
            if request.user != user:
                return redirect('/')
        return render(request, template_name, {'form': form})

    if request.method == 'POST':
        form = form_class(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(reverse('user_profile', args=(pk,)))
        else:
            return render(request, template_name, {'form': form})

def storefront(request):
    total = 5
    currency = "BTC"
    return_url = ""
    description = "Option 1"
    bp = Bitpay()
    response = bp.CreateInvoice(total, currency, return_url, description)

    total = 5
    currency = "BTC"
    return_url = ""
    description = "Option 1"
    bp = Bitpay()
    response = bp.CreateInvoice(total, currency, return_url, description)