from django.urls import path

from userpage.views import *

urlpatterns = [
    path('login', user_login),
    path('insertUser', userinfo_improvement),
    path('getUserAllInfo', get_user_info),
    path('user/feedback', get_user_feedback),
    path('newtask/createtradetask', add_new_trade),
    path('newtask/createinfotask', add_new_activity)
]