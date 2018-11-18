from django.urls import path,re_path

from userpage.views import *

urlpatterns = [
    path('login', user_login),
    path('insertuser', userinfo_improvement),
    path('getuserallinfo', get_user_info),

    path('user/feedback', get_user_feedback),
    path('user/mytask', get_all_task),
    path('user/mycollection', get_all_collection),

    path('newtask/createtradetask', add_new_trade),
    path('newtask/createinfotask', add_new_activity),
    path('image/upload', upload_picture),

    path('trade/gettradenumber', get_valid_good_number),
    path('trade/getall', get_all_goods),
    path('trade/collect', good_collection_changed),
    path('trade/search', get_goods_by_keyword),
    path('trade/comment', add_good_comment),
    path('trade/detail', get_good_detail),

    path('info/getinfonumber', get_valid_good_number),
    path('info/getall', get_all_activities),
    path('info/collect', activity_collection_changed),
    path('info/search', get_activities_by_keyword),
    path('info/comment', add_activity_comment),
    path('info/detail', get_activity_detail),
]