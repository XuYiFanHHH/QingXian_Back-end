# Create your views here.
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import requests
from QingXian.settings import *
from wechat.models import *
import hashlib
import base64
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
            if category != "课外兼职" and category != "婚恋交友" and category != "失物招领" and category != "休闲娱乐":
                category = "其它"
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
        result_list = User.objects.filter(skey=skey)
        if len(result_list) > 0:
            user_id = result_list[0].id
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

# 查看详情
@require_http_methods(["POST"])
def get_activity_or_good_detail(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
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