from django.urls import path

from userpage.views import *

urlpatterns = [
    path('login', user_login),
    path('insertuser', userinfo_improvement),
    path('getuserallinfo', get_user_info),
    path('user/feedback', get_user_feedback),
    path('newtask/createtradetask', add_new_trade),
    path('newtask/createinfotask', add_new_activity),
    path('trade/gettradenumber', get_valid_good_number),
    path('info/getinfonumber', get_valid_good_number),
    path('trade/getall', get_all_goods),
    path('image/upload', upload_picture),
    path('trade/collect', good_collection_changed)
]