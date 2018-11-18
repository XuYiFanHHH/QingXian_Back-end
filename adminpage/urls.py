from django.urls import path

from adminpage.views import *

urlpatterns = [
    path('login', admin_login),
    path('logout', admin_logout),
    path('good/getall', get_all_goods),
    path('good/check', good_check),
    path('good/changecategory', good_change_category)
]