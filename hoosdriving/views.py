from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import authenticate, login
from .forms import *
from django import forms
from django.contrib.auth.models import User
from django.views.generic import View

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

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

def signup(request):
    return render(request, 'signupform.html')