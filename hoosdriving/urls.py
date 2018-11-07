"""hoosdriving URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import url

from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^about/$', views.about),
    url(r'^contact/$', views.contact),
    url(r'^login/$', views.LoginFormView.as_view(), name='login'),
    url(r'^signup/$', views.SignupFormView,name='signup'),
    url(r'^admin/', admin.site.urls),
    url(r'^success/', views.SignupFormView, name='success'),

    url(r'^forgot_password/reset/$', views.reset_password, name='reset_password'),
    url(r'^confirm_password_reset/$', views.confirm_password_reset, name='confirm_password_reset'),
    url(r'^(?P<pk>[0-9]+)/$', login_required(views.UserProfileView.as_view()), name='user_profile'),
    url(r'^(?P<pk>[0-9]+)/update/$', login_required(views.UpdateUserProfileFormView.as_view()),
        name='user_profile_form'),
    url(r'^(?P<pk>[0-9]+)/username/$', views.change_username, name='change_username'),
    url(r'^(?P<pk>[0-9]+)/password/$', views.change_password, name='change_password'),
]
