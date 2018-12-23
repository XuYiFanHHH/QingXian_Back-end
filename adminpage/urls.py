from django.urls import path

from adminpage.views import *

urlpatterns = [
    path('login', admin_login),
    path('logout', admin_logout),
    path('task/get_all', get_all_tasks),
    path('task/get_task_detail', get_task_detail),
    path('task/get_comments', get_comments),
    path('task/check', task_check),
    path('task/change_category', task_change_category),
    path('task/delete_comment', delete_comment),
    path('user/get_user_list', get_user_list),
    path('user/get_detail', get_user_detail),
    path('user/history_task', get_history_tasks),
    path('user/history_comment', get_history_comments),
    path('user/send_msg', send_message),
    path('user/get_feedback', get_user_feedback),
    path('user/feedback_check', admin_check_feedback)
]