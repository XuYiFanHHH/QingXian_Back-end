# Create your views here.
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import requests
from QingXian.settings import *
from wechat.models import *
import hashlib
import base64
import math
import time
import uuid
from codex.baseError import *
# 用户登录接口
@require_http_methods(["POST"])
def user_login(request):
    response = {}
    try:
        code = request.POST["code"]
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        params = {'appid': WECHAT_APPID, 'secret': WECHAT_SECRET, 'js_code': code, 'grant_type': 'authorization_code'}
        wechat_response = requests.get(url, params=params).json()
        openid = wechat_response["openid"]
        session_key = wechat_response["session_key"]
        # 加密
        md5 = hashlib.md5()
        md5.update((openid + session_key).encode("utf8"))
        skey = md5.digest()

        skey = base64.b64encode(skey).decode('utf-8')

        result_list = User.objects.filter(open_id=openid)

        if len(result_list) == 0:
            obj = User(open_id=openid, skey=skey, credit=100, username="", contact_info="")
            obj.save()
        else:
            result_list[0].skey = skey
            result_list[0].save()

        response['skey'] = skey
        response['msg'] = "login success"
        response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
        response['skey'] = ""
    finally:
        response = JsonResponse(response)
        return response

# 完善用户信息,增加头像图片
@require_http_methods(["POST"])
def userinfo_improvement(request):
    response = {}
    try:
        skey = request.POST["skey"]
        result_list = User.objects.filter(skey=skey)

        if len(result_list) > 0:
            result_list[0].username = request.POST['nickName']
            picture = request.POST['avatarUrl']
            result_list[0].save()

            pic_list = Picture.objects.filter(user_id = result_list[0].id)
            if len(pic_list) > 0:
                pic_list[0].picture_url = picture
                pic_list[0].save()
            else:
                obj = Picture(picture_url=picture,
                              pic_count=1,
                              category=2,
                              good_id=-1,
                              activity_id=-1,
                              feedback_id=-1,
                              user_id=result_list[0].id)
                obj.save()
            response['msg'] = "update success"
            response['error'] = 0
        else:
            raise ValidateError("invalid skey, invalid user")
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 返回用户信用分
# 完善用户信息,增加头像图片
@require_http_methods(["POST"])
def get_user_info(request):
    response = {}
    try:
        skey = request.POST["skey"]
        result_list = User.objects.filter(skey=skey)

        if len(result_list) > 0:
            response['credit'] = result_list[0].credit
            response['nickName'] = result_list[0].username
            pic_list = Picture.objects.filter(user_id=result_list[0].id)
            if len(pic_list) > 0:
                response["avatarUrl"] = pic_list[0].picture_url
                response['msg'] = "success"
                response['error'] = 0
            else:
                raise InputError("no avatar error")
        else:
            raise ValidateError("invalid skey, invalid user")
    except Exception as e:
        response['credit'] = -1
        response['nickName'] = ""
        response["avatarUrl"] = ""
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 添加二手交易任务
@require_http_methods(["POST"])
def add_new_trade(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            # 出售或者求购
            label = request.POST["label"]
            # 出售为0
            sale_or_require = 0
            price = 0
            if label == "求购":
                sale_or_require = 1
            elif label == "出售":
                sale_or_require = 0
            else:
                raise InputError("label only accept two kinds of input")
            category = request.POST["category"]
            title = request.POST["title"]
            detail = request.POST["detail"]
            contact_msg = request.POST["notice"]
            client_price_request = request.POST["price"]
            if client_price_request == "面议":
                price = -1
            else:
                price = float(client_price_request)

            new_good = Good(user_id=user_id,
                            title=title,
                            detail=detail,
                            category=category,
                            sale_or_require=sale_or_require,
                            price=price,
                            contact_msg=contact_msg,
                            status=0)
            new_good.save()
            response['msg'] = "success"
            response['error'] = 0
        else:
            raise ValidateError("invalid skey, invalid user")
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 添加信息共享任务
@require_http_methods(["POST"])
def add_new_activity(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            # 出售或者求购
            label = request.POST["label"]
            category = request.POST["category"]
            title = request.POST["title"]
            detail = request.POST["detail"]
            contact_msg = request.POST["notice"]
            freeOrPaid = request.POST["freeOrPaid"]
            price = ""
            price_req=0
            if freeOrPaid == "paid":
                price = request.POST["price"]
                price_req = 1
            elif freeOrPaid == "free":
                price = ""
                price_req = 0
            else:
                raise InputError("free of paid argument error")

            new_activity = Activity(user_id=user_id,
                                    label=label,
                                    title=title,
                                    detail=detail,
                                    category=category,
                                    price_req=price_req,
                                    price=price,
                                    contact_msg=contact_msg,
                                    status=0)
            new_activity.save()
            response['msg'] = "success"
            response['error'] = 0
        else:
            raise ValidateError("invalid skey, invalid user")

    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1

    finally:
        response = JsonResponse(response)
        return response

# 反馈给管理者(先保存到服务器)
@require_http_methods(["POST"])
def get_user_feedback(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            detail = request.POST["info"]
            feedback = Feedback(user_id=user_id, detail=detail)
            feedback.save()
            response['msg'] = "success"
            response['error'] = 0
        else:
            raise ValidateError("invalid skey, invalid user")
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 获取所有已上架二手商品交易总数
@require_http_methods(["POST"])
def get_valid_good_number(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            response["number"] = Good.objects.filter(status = 1).count()
            response["msg"] = "success"
            response["error"]
        else:
            raise ValidateError("invalid skey, invalid user")
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 获取所有已上架信息共享总数
@require_http_methods(["POST"])
def get_valid_info_number(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            response["number"] = Activity.objects.filter(status = 1).count()
            response["msg"] = "success"
            response["error"]
        else:
            raise ValidateError("invalid skey, invalid user")
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 根据页数获取某一些商品
@require_http_methods(["POST"])
def get_all_goods(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            page_id = request.POST["page"]
            total_num = Good.objects.filter(status = 1).count()
            pages = math.ceil(total_num / 10)
            start_num = (page_id - 1) * 10
            end_num = start_num + 10
            if end_num > total_num:
                end_num = total_num

            good_list = list(Good.objects.filter(status = 1).order_by('-release_time')[start_num:end_num])
            return_list = []
            for item in good_list:
                info = {}
                info["good_id"] = item["id"]
                if item["sale_or_require"] == 0:
                    info["label"] = "出售"
                else:
                    info["label"] = "求购"
                info["title"] = item["title"]
                price = item["price"]
                if price == -1:
                    info["price"] = "面议"
                else:
                    info["price"] = str(price)
                info["status"] = item["status"]
                info["user_id"] = item["user_id"]
                pic_list = list(Picture.objects.filter(good_id=item["id"]).order_by(id))
                if len(pic_list) > 0:
                    info["pic_url"] = pic_list[0]
                else:
                    info["pic_url"] = ""

                info["collect_num"] = Collection.objects.filter(good_id = item["id"]).count()
                info["comment_num"] = Comment.objects.filter(good_id = item["id"]).count()
                return_list.append(info)
            response["msg"] = "success"
            response["error"] = 0
        else:
            raise ValidateError("invalid skey, invalid user")
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 上传图片
@require_http_methods(["POST"])
def upload_picture(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            file = request.FILE['pic']
            image_path = '%s/%s%s%s' % (MEDIA_SAVE_ROOT,
                                        str(int(round(time.time() * 1000))),
                                        str(uuid.uuid1()), file.name)
            image_path = image_path.split(".")[0] + ".png"
            with open(image_path, 'wb') as pic:
                for c in file.chunks():
                    pic.write(c)
            print("picture OK", image_path)

            response["msg"] = "success"
            response["error"]
        else:
            raise ValidateError("invalid skey, invalid user")
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response