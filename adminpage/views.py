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
def get_all_goods(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            page_id = int(request.POST["page"])
            status = int(request.POST["status"])
            category = str(request.POST["category"])
            keyword = str(request.POST["keyword"])
            if category != "全部":
                good_list = Good.objects.filter(category=category)
            else:
                good_list = Good.objects.all()
            if status != -1:
                good_list = good_list.filter(status=status)

            good_list = good_list.order_by('-submit_time')

            if keyword != "":
                final_list=[]
                for item in good_list:
                    if item.title.find(keyword) != -1 or item.detail.find(keyword) != -1:
                        final_list.append(item)
            else:
                final_list = good_list

            total_num = len(final_list)
            pages = math.ceil(total_num / 10)

            start_num = (page_id - 1) * 10
            end_num = start_num + 10
            if end_num > total_num:
                end_num = total_num
            #     按page来取数据

            good_list = final_list[start_num:end_num]

            return_list = []
            for item in good_list:
                info = {}
                info["good_id"] = item.id
                if int(item.sale_or_require) == 0:
                    info["label"] = "出售"
                else:
                    info["label"] = "求购"
                info["category"] = item.category
                info["title"] = item.title
                info["content"] = item.detail
                info["contact_msg"] = item.contact_msg
                price = item.price
                if price == -1:
                    info["price"] = "面议"
                else:
                    info["price"] = str(price)
                status = item.status
                if status == 0:
                    info["status"] = "待审核"
                elif status == 1:
                    info["status"] = "已审核发布"
                else:
                    info["status"] = "已下架"

                user_id = item.user_id
                user = User.objects.get(id=user_id)
                info["user_id"] = user_id
                info["nick_name"] = user.username
                info["contact_info"] = user.contact_info

                pic_list = Picture.objects.filter(good_id=item.id)
                pic_url_list = []
                if len(pic_list) > 0:
                    for pic in pic_list:
                        pic_url = pic.picture_url
                        if pic_url.startswith("/home/ubuntu"):
                            pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                        if pic_url != "":
                            pic_url_list.append(pic_url)

                info["pic_urls"] = pic_url_list
                return_list.append(info)

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
def good_check(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            good = Good.objects.get(id = request.POST["good_id"])
            if int(request.POST["agree"]) == 1:
                good.status = 1
                good.release_time = timezone.now()
            else:
                good.status = 2
            good.save()
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
def good_change_category(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            good = Good.objects.get(id = request.POST["good_id"])
            good.category = request.POST["category"]
            good.save()
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response