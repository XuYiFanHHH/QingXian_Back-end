from django.urls import path

from userpage.views import *

urlpatterns = [
    path('login', user_login),
]