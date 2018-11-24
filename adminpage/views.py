# Create your views here.
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from codex.baseError import *
from wechat.models import *
from QingXian.settings import *
import math
@require_http_methods(["POST"])
def admin_login(request):
    response = {}
    try:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            raise ValidateError("Login failed!")
        response['msg'] = "Login success!"
        response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

@require_http_methods(["POST"])
def admin_logout(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            logout(request)
            response['msg'] = "Logout success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 获取商品数据，-1:所有的，0：待审核，1：审核通过，已发布；2：已下架
@require_http_methods(["POST"])
def get_all_tasks(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            page_id = int(request.POST["page"])
            status = int(request.POST["status"])
            category = str(request.POST["category"])
            keyword = str(request.POST["keyword"])
            goods_or_activity = int(request.POST["goods_or_activity"])
            task_list = Task.objects.filter(goods_or_activity=goods_or_activity)
            if category != "全部":
                task_list = task_list.filter(category=category)
            if status != -1:
                task_list = task_list.filter(status=status)

            task_list = task_list.order_by('-submit_time')

            if keyword != "":
                final_list=[]
                for item in task_list:
                    if item.title.find(keyword) != -1 or item.detail.find(keyword) != -1:
                        final_list.append(item)
            else:
                final_list = task_list

            total_num = len(final_list)
            pages = math.ceil(total_num / 10)
            start_num = (page_id - 1) * 10
            if start_num <= total_num:
                end_num = start_num + 10
                if end_num > total_num:
                    end_num = total_num
                task_list = final_list[start_num:end_num]
            else:
                task_list = []
            return_list = []
            for item in task_list:
                task = {}
                task["task_id"] = item.id
                task["label"] = item.label
                task["category"] = item.category
                task["title"] = item.title
                task["content"] = item.detail
                task["contact_msg"] = item.contact_msg
                price = item.price
                if price == -1:
                    task["price"] = "面议"
                else:
                    price = format(price, '.2f')
                    task["price"] = str(price)
                status = item.status
                if status == 0:
                    task["status"] = "待审核"
                elif status == 1:
                    task["status"] = "已审核发布"
                else:
                    task["status"] = "已下架"

                user_id = item.user_id
                user = User.objects.get(id=user_id)
                task["user_id"] = user_id
                task["nickname"] = user.nickname
                task["user_contact"] = user.contact_info
                # 相关图片
                pic_list = Picture.objects.filter(task_id=item.id)
                pic_url_list = []
                if len(pic_list) > 0:
                    for pic in pic_list:
                        pic_url = pic.picture_url
                        if pic_url.startswith("/home/ubuntu"):
                            pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                        if pic_url != "":
                            pic_url_list.append(pic_url)
                task["pics"] = pic_url_list
                # 相关评论
                comment_list = []
                comments = Comment.objects.filter(task_id=item.id)
                for comment in comments:
                    return_comment = {}
                    return_comment["reviewer_id"] = comment.reviewer_id
                    return_comment["reviewer_nickname"] = User.objects.get(id=comment.reviewer_id).nickname
                    return_comment["receiver_id"] = comment.receiver_id
                    return_comment["receiver_nickname"] = User.objects.get(id=comment.receiver_id).nickname
                    return_comment["detail"] = comment.detail
                    return_comment["time"] = str(comment.release_time.strftime('%Y-%m-%d %H:%M'))
                    comment_list.append(return_comment)
                task["comment_list"] = comment_list
                return_list.append(task)

            response["datalist"] = return_list
            response["pages"] = pages
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 上架或者下架
@require_http_methods(["POST"])
def task_check(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            task = Task.objects.get(id=int(request.POST["task_id"]))
            if int(request.POST["agree"]) == 1:
                task.status = 1
                task.release_time = timezone.now()
            else:
                task.status = 2
            task.save()
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 修改商品分类
@require_http_methods(["POST"])
def task_change_category(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            task = Task.objects.get(id=int(request.POST["task_id"]))
            task.category = request.POST["category"]
            task.save()
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response