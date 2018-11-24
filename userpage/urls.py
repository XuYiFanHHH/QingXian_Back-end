from django.urls import path,re_path

from userpage.views import *

urlpatterns = [
    path('login', user_login),
    path('insert_user', insert_user),
    path('user/get_user_info', get_user_info),
    path('user/update_user_info', update_user_info),
    path('user/get_user_contact', get_user_contact),

    path('user/feedback', get_user_feedback),
    path('user/my_task', get_all_task),
    path('user/my_collection', get_all_collection),

    path('create_task', add_new_task),
    path('image/upload', upload_picture),

    path('task/get_number', get_valid_task_number),
    path('task/get_all', get_tasks),
    path('task/detail', get_task_detail),
    path('task/collect', task_collection_changed),
    path('task/comment', add_comment),
]