from django.urls import path

from adminpage.views import *

urlpatterns = [
    path('login', admin_login),
    path('logout', admin_logout),
    path('task/get_all', get_all_tasks),
    path('task/check', task_check),
    path('task/change_category', task_change_category),
]