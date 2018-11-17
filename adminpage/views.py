# Create your views here.
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from codex.baseError import *
from wechat.models import *
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
        if not request.user.is_authenticated():
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
def get_all_goods(request):
    response = {}
    try:
        if not request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            page_id = request.POST["page"]
            total_num = Good.objects.all().count()
            pages = math.ceil(total_num / 10)

            start_num = (page_id - 1) * 10
            end_num = start_num + 10
            if end_num > total_num:
                end_num = total_num
            #     按page来取数据
            status = int(request.POST["status"])
            if status == -1:
                good_list = list(Good.objects.order_by('-submit_time')[start_num:end_num])
            else:
                good_list = list(Good.objects.filter(status = status)
                                 .order_by('-submit_time')[start_num:end_num])
            return_list = []
            for item in good_list:
                info = {}
                info["good_id"] = item["id"]
                if item["sale_or_require"] == 0:
                    info["label"] = "出售"
                else:
                    info["label"] = "求购"
                info["category"] = item["category"]
                info["title"] = item["title"]
                info["content"] = item["detail"]
                info["contact_msg"] = item["contact_msg"]
                info["price"] = item["price"]
                info["status"] = item["status"]

                user_id = item["user_id"]
                user = User.objects.get(id=user_id)
                info["user_id"] = user_id
                info["nick_name"] = user.username
                info["contact_info"] = user.contact_info

                pic_list = list(Picture.objects.filter(good_id = item["id"]))
                info["pic_urls"] = pic_list
                return_list.append(info)

            response["datalist"] = return_list
            response["pages"] = pages
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
        response = JsonResponse(response)
    finally:
        response = JsonResponse(response)
        return response

@require_http_methods(["POST"])
def good_check(request):
    response = {}
    try:
        if not request.user.is_authenticated():
            raise ValidateError("admin-user not login!")
        else:
            good = Good.objects.get(id = request.POST["good_id"])
            if int(request["agree"]) == 1:
                good.status = 1
                good.release_time = timezone.now()
            else:
                good.status = 0
            good.save()
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response