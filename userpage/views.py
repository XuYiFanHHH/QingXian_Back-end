# Create your views here.
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import requests
from QingXian.settings import *
from wechat.models import *
import hashlib
import base64

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
        response = JsonResponse(response)
    except Exception as e:
        response['msg'] = str(e)
        print("error: ", str(e))
        response['error'] = 1
        response['skey'] = ""
        response = JsonResponse(response)
    finally:
        return response

# 完善用户信息,增加头像图片
@require_http_methods(["POST"])
def userinfo_improvement(request):
    response = {}
    try:
        skey = request.POST["skey"]
        result_list = User.objects.filter(skey=skey)

        if len(result_list) > 0:
            result_list[0].usernam=request.POST['nickName']
            result_list[0].save()
            obj = Picture(picture_url=request.POST['avatarUrl'],
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
            response['msg'] = "skey invalid"
            response['error'] = 1
        response = JsonResponse(response)
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
        response = JsonResponse(response)
    finally:
        return response

# 返回用户信用分
# 完善用户信息,增加头像图片
@require_http_methods(["POST"])
def get_user_credit(request):
    response = {}
    try:
        skey = request.POST["skey"]
        result_list = User.objects.filter(skey=skey)

        if len(result_list) > 0:
            response['credit'] = result_list[0].credit
            response['msg'] = "success"
            response['error'] = 0
        else:
            response['credit'] = -1
            response['msg'] = "skey invalid"
            response['error'] = 1
        response = JsonResponse(response)
    except Exception as e:
        response['credit'] = -1
        response['msg'] = str(e)
        response['error'] = 1
        response = JsonResponse(response)
    finally:
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
            response['msg'] = "skey invalid"
            response['error'] = 1
        response = JsonResponse(response)
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
        response = JsonResponse(response)
    finally:
        return response

# 查看详情
@require_http_methods(["POST"])
def get_activity_or_good_detail(request):
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
            response['msg'] = "skey invalid"
            response['error'] = 1
        response = JsonResponse(response)
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
        response = JsonResponse(response)
    finally:
        return response