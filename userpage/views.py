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

# 添加用户联系信息
@require_http_methods(["POST"])
def update_user_contact_info(request):
    response = {}
    try:
        skey = request.POST["skey"]
        result_list = User.objects.filter(skey=skey)
        if len(result_list) > 0:
            contact_info = request.POST["contact_info"]
            result_list[0].contact_info = contact_info
            result_list[0].save()
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

# 获取用户联系信息
@require_http_methods(["POST"])
def get_user_contact_info(request):
    response = {}
    try:
        skey = request.POST["skey"]
        result_list = User.objects.filter(skey=skey)
        if len(result_list) > 0:
            contact_info = result_list[0].contact_info
            print("info: ", contact_info)
            response["contact_info"] = contact_info
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

# 返回用户信用分,用户信息,头像图片
@require_http_methods(["POST"])
def get_user_info(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        response['credit'] = user.credit
        response['nickName'] = user.username
        avatar_url = str(Picture.objects.get(user_id=user.id).picture_url)
        if avatar_url.startswith("/home/"):
            avatar_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + avatar_url
        response["avatarUrl"] = avatar_url
        response['msg'] = "success!"
        response['error'] = 0
    except Exception as e:
        response['credit'] = -1
        response['nickName'] = ""
        response["avatarUrl"] = ""
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

            split_list = request.POST["pics"].split(",")
            pic_list = []
            for pic in split_list:
                if pic:
                    pic_list.append(pic)
            pic_count = 1
            for pic in pic_list:
                picture = Picture(picture_url=pic,
                                  pic_count=pic_count,
                                  category=3,
                                  good_id=-1,
                                  activity_id=-1,
                                  user_id=-1,
                                  feedback_id=feedback.id
                                  )
                picture.save()
                pic_count += 1
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

# 添加二手交易任务
@require_http_methods(["POST"])
def add_new_trade(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            user_credit = user_list[0].credit
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
                            status=0,
                            user_credit=user_credit)
            new_good.save()
            split_list = request.POST["pics"].split(",")
            pic_list = []
            for pic in split_list:
                if pic:
                    pic_list.append(pic)
            pic_count = 1
            for pic in pic_list:
                picture = Picture(picture_url=pic,
                                  pic_count=pic_count,
                                  category=0,
                                  good_id=new_good.id,
                                  activity_id=-1,
                                  user_id=-1,
                                  feedback_id=-1
                                  )
                picture.save()
                pic_count += 1
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
            user_credit = user_list[0].credit
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
                                    status=0,
                                    user_credit=user_credit)
            new_activity.save()
            split_list = request.POST["pics"].split(",")
            pic_list = []
            for pic in split_list:
                if pic:
                    pic_list.append(pic)
            pic_count = 1
            for pic in pic_list:
                picture = Picture(picture_url=pic,
                                  pic_count=pic_count,
                                  category=1,
                                  good_id=-1,
                                  activity_id=new_activity.id,
                                  user_id=-1,
                                  feedback_id=-1
                                  )
                picture.save()
                pic_count += 1
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
            response["error"] = 0
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
            response["error"] = 0
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
            user_id = user_list[0].id
            page_id = int(request.POST["currentPage"])
            currentTab = int(request.POST["currentTab"])
            selectIndex = int(request.POST["selectIndex"])
            sortIndex = int(request.POST["sortIndex"])
            # 从已上架的商品中筛选
            good_list = Good.objects.filter(status = 1)
            if currentTab == 1:
                good_list = good_list.filter(category="学习")
            elif currentTab == 2:
                good_list = good_list.filter(category="日用")
            elif currentTab == 3:
                good_list = good_list.filter(category="服饰")
            elif currentTab == 4:
                good_list = good_list.filter(category="运动")
            elif currentTab == 5:
                good_list = good_list.filter(category="电子")
            elif currentTab == 6:
                good_list = good_list.filter(category="美妆")
            elif currentTab == 7:
                good_list = good_list.filter(category="其它")

            if selectIndex == 1:
                good_list = good_list.filter(sale_or_require=0)
            elif selectIndex == 2:
                good_list = good_list.filter(sale_or_require=1)

            if sortIndex == 0:
                good_list = good_list.order_by('-release_time')
            elif sortIndex == 1:
                good_list = good_list.order_by('release_time')
            elif sortIndex == 2:
                good_list = good_list.order_by('-price')
            elif sortIndex == 3:
                good_list = good_list.order_by('price')
            elif sortIndex == 4:
                good_list = good_list.order_by('-user_credit')

            total_num = good_list.count()
            start_num = (page_id - 1) * 10
            if start_num <= total_num:
                end_num = start_num + 10
                if end_num > total_num:
                    end_num = total_num

                good_list = good_list[start_num:end_num]
                return_list = []
                for item in good_list:
                    info = {}
                    info["good_id"] = item.id
                    select_result = Collection.objects.filter(user_id=user_id, good_id=item.id)
                    if len(select_result) > 0:
                        info["collect"] = 1
                    else:
                        info["collect"] = 0
                    if int(item.sale_or_require) == 0:
                        info["label"] = "出售"
                    else:
                        info["label"] = "求购"
                    info["title"] = item.title
                    price = item.price
                    if price == -1:
                        info["price"] = "面议"
                    else:
                        price = format(price, '.2f')
                        info["price"] = str(price)
                    info["user_id"] = item.user_id
                    pic_list = Picture.objects.filter(good_id=item.id).order_by("id")
                    if len(pic_list) > 0:
                        pic_url = str(pic_list[0].picture_url)
                    if len(pic_list) == 0 or pic_url == "":
                        pic_url = '%s/%s' % (PIC_SAVE_ROOT,"default_image.png")

                    if pic_url.startswith("/home/ubuntu"):
                        pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url

                    info["pic_url"] = pic_url
                    info["user_credit"] = item.user_credit
                    info["collect_num"] = Collection.objects.filter(good_id = item.id).count()
                    info["comment_num"] = Comment.objects.filter(good_id = item.id).count()
                    return_list.append(info)
            else:
                return_list = []
            response["datalist"] = return_list
            response["msg"] = "success"
            response["error"] = 0
            print(response)
        else:
            raise ValidateError("invalid skey, invalid user")
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 根据页数获取某一些活动 （selectIndex未沟通）
@require_http_methods(["POST"])
def get_all_activities(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            page_id = int(request.POST["currentPage"])
            currentTab = int(request.POST["currentTab"])
            selectIndex = int(request.POST["selectIndex"])
            sortIndex = int(request.POST["sortIndex"])
            # 从已上架的活动中筛选
            activity_list = Activity.objects.filter(status=1)
            if currentTab == 1:
                activity_list = activity_list.filter(category="课外兼职")
            elif currentTab == 2:
                activity_list = activity_list.filter(category="婚恋交友")
            elif currentTab == 3:
                activity_list = activity_list.filter(category="失物招领")
            elif currentTab == 4:
                activity_list = activity_list.filter(category="休闲娱乐")
            elif currentTab == 5:
                activity_list = activity_list.filter(category="公共活动")
            elif currentTab == 6:
                activity_list = activity_list.filter(category="其它")

            if selectIndex == 1:
                activity_list = activity_list.filter(price_req=0)
            elif selectIndex == 2:
                activity_list = activity_list.filter(price_req=1)

            if sortIndex == 0:
                activity_list = activity_list.order_by('-release_time')
            elif sortIndex == 1:
                activity_list = activity_list.order_by('release_time')
            elif sortIndex == 2:
                activity_list = activity_list.order_by('-user_credit')

            total_num = activity_list.count()
            start_num = (page_id - 1) * 10
            if start_num <= total_num:
                end_num = start_num + 10
                if end_num > total_num:
                    end_num = total_num
                activity_list = activity_list[start_num:end_num]
                return_list = []
                for item in activity_list:
                    info = {}
                    info["activity_id"] = item.id
                    select_result = Collection.objects.filter(user_id=user_id, activity_id=item.id)
                    if len(select_result) > 0:
                        info["collect"] = 1
                    else:
                        info["collect"] = 0
                    info["label"] = item.label
                    info["title"] = item.title
                    if item.price_req == 1:
                        info["price"] = item.price
                    else:
                        info["price"] = "无价位要求"

                    info["user_id"] = item.user_id
                    info["user_credit"] = item.user_credit
                    pic_list = Picture.objects.filter(activity_id=item.id).order_by("id")
                    if len(pic_list) > 0:
                        pic_url = str(pic_list[0].picture_url)
                    if len(pic_list) == 0 or pic_url == "":
                        pic_url = '%s/%s' % (PIC_SAVE_ROOT,"default_image.png")

                    if pic_url.startswith("/home/ubuntu"):
                        pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url

                    info["pic_url"] = pic_url
                    info["collect_num"] = Collection.objects.filter(activity_id=item.id).count()
                    info["comment_num"] = Comment.objects.filter(activity_id=item.id).count()
                    return_list.append(info)
            else:
                return_list = []
            response["datalist"] = return_list
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

# 根据页数与关键词获取某一些商品
@require_http_methods(["POST"])
def get_goods_by_keyword(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            page_id = int(request.POST["currentPage"])
            keyword = str(request.POST["keyword"])
            # 0发售和求购1只看发售2只看求购
            selectIndex = int(request.POST["selectIndex"])
            # 0发布时间降序1发布时间升序2价格降序3价格升序4信用降序
            sortIndex = int(request.POST["sortIndex"])
            # 从已上架的商品中筛选
            good_list = Good.objects.filter(status=1)
            if selectIndex == 1:
                good_list = good_list.filter(sale_or_require=0)
            elif selectIndex == 2:
                good_list = good_list.filter(sale_or_require=1)

            if sortIndex == 0:
                good_list = good_list.order_by('-release_time')
            elif sortIndex == 1:
                good_list = good_list.order_by('release_time')
            elif sortIndex == 2:
                good_list = good_list.order_by('-price')
            elif sortIndex == 3:
                good_list = good_list.order_by('price')
            elif sortIndex == 4:
                good_list = good_list.order_by('-user_credit')

            if keyword != "":
                final_list = []
                for item in good_list:
                    if item.title.find(keyword) != -1 or item.detail.find(keyword) != -1:
                        final_list.append(item)
            else:
                final_list = good_list

            total_num = len(final_list)
            start_num = (page_id - 1) * 10
            if start_num <= total_num:
                end_num = start_num + 10
                if end_num > total_num:
                    end_num = total_num

                good_list = final_list[start_num:end_num]
                return_list = []
                for item in good_list:
                    info = {}
                    info["good_id"] = item.id
                    select_result = Collection.objects.filter(user_id=user_id, good_id=item.id)
                    if len(select_result) > 0:
                        info["collect"] = 1
                    else:
                        info["collect"] = 0
                    if int(item.sale_or_require) == 0:
                        info["label"] = "出售"
                    else:
                        info["label"] = "求购"
                    info["title"] = item.title
                    price = item.price
                    if price == -1:
                        info["price"] = "面议"
                    else:
                        price = format(price, '.2f')
                        info["price"] = str(price)
                    info["user_id"] = item.user_id
                    pic_list = Picture.objects.filter(good_id=item.id).order_by("id")
                    if len(pic_list) > 0:
                        pic_url = str(pic_list[0].picture_url)
                    if len(pic_list) == 0 or pic_url == "":
                        pic_url = '%s/%s' % (PIC_SAVE_ROOT,"default_image.png")

                    if pic_url.startswith("/home/ubuntu"):
                        pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url

                    info["pic_url"] = pic_url
                    info["user_credit"] = item.user_credit
                    info["collect_num"] = Collection.objects.filter(good_id=item.id).count()
                    info["comment_num"] = Comment.objects.filter(good_id=item.id).count()
                    return_list.append(info)
            else:
                return_list = []
            response["datalist"] = return_list
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

# 根据页数与关键词获取某一些活动 （selectIndex未沟通）
@require_http_methods(["POST"])
def get_activities_by_keyword(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            page_id = int(request.POST["currentPage"])
            keyword = str(request.POST["keyword"])
            # 0全部1只看无价格要求的2只看有价格要求
            selectIndex = int(request.POST["selectIndex"])
            # 0发布时间降序1发布时间升序2信用降序
            sortIndex = int(request.POST["sortIndex"])
            # 从已上架的商品中筛选
            activity_list = Activity.objects.filter(status=1)
            if selectIndex == 1:
                activity_list = activity_list.filter(price_req=0)
            elif selectIndex == 2:
                activity_list = activity_list.filter(price_req=1)

            if sortIndex == 0:
                activity_list = activity_list.order_by('-release_time')
            elif sortIndex == 1:
                activity_list = activity_list.order_by('release_time')
            elif sortIndex == 2:
                activity_list = activity_list.order_by('-user_credit')

            if keyword != "":
                final_list = []
                for item in activity_list:
                    if item.title.find(keyword) != -1 or item.detail.find(keyword) != -1\
                            or item.label.find(keyword) != -1:
                        final_list.append(item)
            else:
                final_list = activity_list

            total_num = len(final_list)
            start_num = (page_id - 1) * 10
            if start_num <= total_num:
                end_num = start_num + 10
                if end_num > total_num:
                    end_num = total_num

                activity_list = final_list[start_num:end_num]
                return_list = []
                for item in activity_list:
                    info = {}
                    info["activity_id"] = item.id
                    select_result = Collection.objects.filter(user_id=user_id, activity_id=item.id)
                    if len(select_result) > 0:
                        info["collect"] = 1
                    else:
                        info["collect"] = 0
                    info["label"] = item.label
                    info["title"] = item.title
                    if item.price_req == 1:
                        info["price"] = item.price
                    else:
                        info["price"] = "无价位要求"

                    info["user_id"] = item.user_id
                    info["user_credit"] = item.user_credit

                    pic_list = Picture.objects.filter(activity_id=item.id).order_by("id")
                    if len(pic_list) > 0:
                        pic_url = str(pic_list[0].picture_url)
                    if len(pic_list) == 0 or pic_url == "":
                        pic_url = '%s/%s' % (PIC_SAVE_ROOT,"default_image.png")

                    if pic_url.startswith("/home/ubuntu"):
                        pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url

                    info["pic_url"] = pic_url
                    info["collect_num"] = Collection.objects.filter(activity_id=item.id).count()
                    info["comment_num"] = Comment.objects.filter(activity_id=item.id).count()
                    return_list.append(info)
            else:
                return_list = []
            response["datalist"] = return_list
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

# 二手商品收藏与取消收藏
@require_http_methods(["POST"])
def good_collection_changed(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            good_id = int(request.POST["id"])

            collect_result = Collection.objects.filter(user_id=user_id, good_id=good_id)
            if len(collect_result) > 0:
                collect_result.delete()
                response["hasCollect"] = 0
            else:
                collection = Collection(user_id=user_id,
                                        category=0,
                                        good_id=good_id,
                                        activity_id=-1,
                                        )
                collection.save()
                response["hasCollect"] = 1
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

# 活动消息收藏与取消收藏
@require_http_methods(["POST"])
def activity_collection_changed(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            activity_id = int(request.POST["id"])

            collect_result = Collection.objects.filter(user_id=user_id, activity_id=activity_id)
            if len(collect_result) > 0:
                collect_result.delete()
                response["hasCollect"] = 0
            else:
                collection = Collection(user_id=user_id,
                                        category=1,
                                        good_id=-1,
                                        activity_id=activity_id,
                                        )
                collection.save()
                response["hasCollect"] = 1
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

# 二手商品添加评论
@require_http_methods(["POST"])
def add_good_comment(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            good_id = int(request.POST["id"])
            receiver_id = int(request.POST["receiver_id"])
            detail = str(request.POST["detail"])
            comment = Comment(reviewer_id=user_id,
                              receiver_id=receiver_id,
                              detail=detail,
                              category=0,
                              good_id=good_id,
                              activity_id=-1
                              )
            comment.save()
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

# 活动信息添加评论
@require_http_methods(["POST"])
def add_activity_comment(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            activity_id = int(request.POST["id"])
            receiver_id = int(request.POST["receiver_id"])
            detail = str(request.POST["detail"])
            comment = Comment(reviewer_id=user_id,
                              receiver_id=receiver_id,
                              detail=detail,
                              category=1,
                              good_id=-1,
                              activity_id=activity_id
                              )
            comment.save()
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

# 二手商品查看详情
@require_http_methods(["POST"])
def get_good_detail(request):
    response = {}
    try:
        skey = str(request.POST["skey"])
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            good_id = int(request.POST["id"])
            good = Good.objects.get(id=good_id)
            if good.sale_or_require == 0:
                response["label"] = "出售"
            else:
                response["label"] = "求购"
            response["category"] = good.category
            response["title"] = good.title
            response["detail"] = good.detail
            price = good.price
            if price == -1:
                response["price"] = "面议"
            else:
                price = format(price, '.2f')
                response["price"] = price
            response["contact_msg"] = good.contact_msg

            response["user_id"] = good.user_id
            select_result = Collection.objects.filter(user_id=user_id, good_id=good.id)
            if len(select_result) > 0:
                response["hasCollect"] = 1
            else:
                response["hasCollect"] = 0
            publisher = User.objects.get(id=good.user_id)
            response["user_contact_info"] = publisher.contact_info
            response["user_credit"] = publisher.credit
            response["nickname"] = publisher.username

            avatar_url = str(Picture.objects.get(user_id=good.user_id).picture_url)
            if avatar_url.startswith("/home/"):
                avatar_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + avatar_url
            response["avatar"] = avatar_url
            # 任务相关图片
            pic_list = Picture.objects.filter(good_id=good_id)
            pic_url_list = []
            if len(pic_list) > 0:
                for pic in pic_list:
                    pic_url = pic.picture_url
                    if pic_url.startswith("/home/ubuntu"):
                        pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                    if pic_url != "":
                        pic_url_list.append(pic_url)

            if len(pic_url_list) == 0:
                pic_url = '%s/%s' % (PIC_SAVE_ROOT,"default_image.png")
                pic_url_list.append(str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url)
            response["pic_list"] = pic_url_list

            # 相关评论
            comment_list = []
            comments = Comment.objects.filter(good_id=good_id)
            for comment in comments:
                return_comment = {}
                return_comment["id"] = comment.id
                return_comment["reviewer_id"] = comment.reviewer_id
                return_comment["reviewer_nickname"] = User.objects.get(id=comment.reviewer_id).username
                return_comment["receiver_id"] = comment.receiver_id
                return_comment["receiver_nickname"] = User.objects.get(id=comment.receiver_id).username
                return_comment["detail"] = comment.detail
                return_comment["time"] = str(comment.release_time.strftime('%Y-%m-%d %H:%M'))
                comment_list.append(return_comment)

            response["comment_list"] = comment_list
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

# 信息共享查看详情
@require_http_methods(["POST"])
def get_activity_detail(request):
    response = {}
    try:
        skey = str(request.POST["skey"])
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            user_id = user_list[0].id
            activity_id = int(request.POST["id"])
            activity = Activity.objects.get(id=activity_id)
            response["label"] = activity.label
            response["category"] = activity.category
            response["title"] = activity.title
            response["detail"] = activity.detail
            if activity.price_req == 1:
                response["price"] = activity.price
            else:
                response["price"] = "无价位要求"
            response["contact_msg"] = activity.contact_msg

            response["user_id"] = activity.user_id
            select_result = Collection.objects.filter(user_id=user_id, activity_id=activity.id)
            if len(select_result) > 0:
                response["hasCollect"] = 1
            else:
                response["hasCollect"] = 0
            publisher = User.objects.get(id=activity.user_id)
            response["user_contact_info"] = publisher.contact_info
            response["user_credit"] = publisher.credit
            response["nickname"] = publisher.username

            avatar_url = str(Picture.objects.get(user_id=activity.user_id).picture_url)
            if avatar_url.startswith("/home/"):
                avatar_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + avatar_url
            response["avatar"] = avatar_url
            # 任务相关图片
            pic_list = Picture.objects.filter(activity_id=activity_id)
            pic_url_list = []
            if len(pic_list) > 0:
                for pic in pic_list:
                    pic_url = pic.picture_url
                    if pic_url.startswith("/home/ubuntu"):
                        pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                    if pic_url != "":
                        pic_url_list.append(pic_url)

            if len(pic_url_list) == 0:
                pic_url = '%s/%s' % (PIC_SAVE_ROOT,"default_image.png")
                pic_url_list.append(str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url)
            response["pic_list"] = pic_url_list

            # 相关评论
            comment_list = []
            comments = Comment.objects.filter(activity_id=activity_id)
            for comment in comments:
                return_comment = {}
                return_comment["id"] = comment.id
                return_comment["reviewer_id"] = comment.reviewer_id
                return_comment["reviewer_nickname"] = User.objects.get(id=comment.reviewer_id).username
                return_comment["receiver_id"] = comment.receiver_id
                return_comment["receiver_nickname"] = User.objects.get(id=comment.receiver_id).username
                return_comment["detail"] = comment.detail
                return_comment["time"] = str(comment.release_timestrftime('%Y-%m-%d %H:%M'))
                comment_list.append(return_comment)

            response["comment_list"] = comment_list
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

# 查看自己已发布的全部任务
@require_http_methods(["POST"])
def get_all_task(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        category = int(request.POST["category"])
        status = int(request.POST["status"])
        page_id = int(request.POST["page"])
        task_list = []
        if category == 0:
            all_task = Good.objects.filter(user_id=user.id)
            if status != -1:
                all_task = all_task.filter(status=status)

            total_num = all_task.count()
            start_num = (page_id - 1) * 10
            if start_num <= total_num:
                end_num = start_num + 10
                if end_num > total_num:
                    end_num = total_num
                all_task = all_task.order_by("-submit_time")[start_num:end_num]
            else:
                all_task = []

            for item in all_task:
                task = {}
                task["task_id"] = item.id
                task["title"] = item.title
                task["category"] = item.category
                task["status"] = item.status
                if item.sale_or_require == 0:
                    task["label"] = "出售"
                else:
                    task["label"] = "求购"
                price = item.price
                if price == -1:
                    task["price"] = "面议"
                else:
                    price = format(price, '.2f')
                    task["price"] = price

                pic_list = Picture.objects.filter(good_id=item.id)
                if len(pic_list) > 0:
                    pic_url = str(pic_list[0].picture_url)
                if len(pic_list) == 0 or pic_url == "":
                    pic_url = '%s/%s' % (PIC_SAVE_ROOT, "default_image.png")
                if pic_url.startswith("/home/ubuntu"):
                    pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                task["pic_url"] = pic_url
                task["collect_num"] = Collection.objects.filter(good_id=item.id).count()
                task["comment_num"] = Comment.objects.filter(good_id=item.id).count()
                task_list.append(task)
        elif category == 1:
            all_task = Activity.objects.filter(user_id=user.id)
            if status != -1:
                all_task = all_task.filter(status=status)

            total_num = all_task.count()
            start_num = (page_id - 1) * 10
            if start_num <= total_num:
                end_num = start_num + 10
                if end_num > total_num:
                    end_num = total_num
                all_task = all_task.order_by("-submit_time")[start_num:end_num]
            else:
                all_task = []

            for item in all_task:
                task = {}
                task["task_id"] = item.id
                task["title"] = item.title
                task["category"] = item.category
                task["label"] = item.label
                task["status"] = item.status
                if item.price_req == 1:
                    task["price"] = item.price
                else:
                    task["price"] = "无价位要求"
                pic_list = Picture.objects.filter(activity_id=item.id)
                if len(pic_list) > 0:
                    pic_url = str(pic_list[0].picture_url)
                if len(pic_list) == 0 or pic_url == "":
                    pic_url = '%s/%s' % (PIC_SAVE_ROOT, "default_image.png")

                if pic_url.startswith("/home/ubuntu"):
                    pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                task["pic_url"] = pic_url
                task["collect_num"] = Collection.objects.filter(activity_id=item.id).count()
                task["comment_num"] = Comment.objects.filter(activity_id=item.id).count()
                task_list.append(task)
        response["taskList"] = task_list
        response['msg'] = "success！"
        response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 查看自己已发布的全部任务
@require_http_methods(["POST"])
def get_my_all_task(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        status = int(request.POST["status"])
        page_id = int(request.POST["page"])
        all_task = []
        all_task_index = []
        task_list = []
        all_good_task = Good.objects.filter(user_id=user.id)
        all_activity_task = Activity.objects.filter(user_id=user.id)
        if status != -1:
            all_good_task = all_good_task.filter(status=status)
            all_activity_task = all_activity_task.filter(status=status)
        all_good_task = all_good_task.order_by("-submit_time")
        all_activity_task = all_activity_task.order_by("-submit_time")
        good_length = len(all_good_task)
        activity_length = len(all_activity_task)
        j = 0
        i = 0
        while i < good_length and j < activity_length:
            if all_good_task[i].submit_time >= all_activity_task[j].submit_time:
                all_task.append(all_good_task[i])
                all_task_index.append(0)
                i += 1
            else:
                all_task.append(all_activity_task[j])
                all_task_index.append(1)
                j += 1
        if i < good_length:
            for k in range(i, good_length):
                all_task.append(all_good_task[k])
                all_task_index.append(0)
        else:
            for k in range(j, activity_length):
                all_task.append(all_activity_task[k])
                all_task_index.append(1)

        total_num = len(all_task)
        start_num = (page_id - 1) * 10
        if start_num <= total_num:
            end_num = start_num + 10
            if end_num > total_num:
                end_num = total_num
            all_task = all_task[start_num:end_num]
            all_task_index = all_task_index[start_num:end_num]
        else:
            all_task = []

        for item in all_task:
            task = {}
            task["task_id"] = item.id
            task["title"] = item.title
            task["category"] = item.category
            task["status"] = item.status
            if all_task_index[all_task.index(item)] == 0:
                task["good_or_activity"] = 0
                if item.sale_or_require == 0:
                    task["label"] = "出售"
                else:
                    task["label"] = "求购"
                price = item.price
                if price == -1:
                    task["price"] = "面议"
                else:
                    price = format(price, '.2f')
                    task["price"] = price

                pic_list = Picture.objects.filter(good_id=item.id)
                if len(pic_list) > 0:
                    pic_url = str(pic_list[0].picture_url)
                if len(pic_list) == 0 or pic_url == "":
                    pic_url = '%s/%s' % (PIC_SAVE_ROOT, "default_image.png")
                if pic_url.startswith("/home/ubuntu"):
                    pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                task["pic_url"] = pic_url
                task["collect_num"] = Collection.objects.filter(good_id=item.id).count()
                task["comment_num"] = Comment.objects.filter(good_id=item.id).count()
                task_list.append(task)
            else:
                task["good_or_activity"] = 1
                task["label"] = item.label
                if item.price_req == 1:
                    task["price"] = item.price
                else:
                    task["price"] = "无价位要求"
                pic_list = Picture.objects.filter(activity_id=item.id)
                if len(pic_list) > 0:
                    pic_url = str(pic_list[0].picture_url)
                if len(pic_list) == 0 or pic_url == "":
                    pic_url = '%s/%s' % (PIC_SAVE_ROOT, "default_image.png")

                if pic_url.startswith("/home/ubuntu"):
                    pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                task["pic_url"] = pic_url
                task["collect_num"] = Collection.objects.filter(activity_id=item.id).count()
                task["comment_num"] = Comment.objects.filter(activity_id=item.id).count()
                task_list.append(task)
        response["taskList"] = task_list
        response['msg'] = "success！"
        response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response

# 查看自己的全部收藏
@require_http_methods(["POST"])
def get_all_collection(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        category = int(request.POST["category"])
        page_id = int(request.POST["page"])
        collections = Collection.objects.filter(user_id=user.id).filter(category=category).order_by("-release_time")
        total_num = collections.count()
        start_num = (page_id - 1) * 10
        if start_num <= total_num:
            end_num = start_num + 10
            if end_num > total_num:
                end_num = total_num
            collections = collections[start_num:end_num]
        else:
            collections = []

        task_list = []
        if category == 0:
            for item in collections:
                good_id = item.good_id
                item = Good.objects.get(id=good_id)
                task = {}
                task["task_id"] = item.id
                task["title"] = item.title
                task["category"] = item.category
                task["status"] = item.status
                if item.sale_or_require == 0:
                    task["label"] = "出售"
                else:
                    task["label"] = "求购"
                price = item.price
                if price == -1:
                    task["price"] = "面议"
                else:
                    price = format(price, '.2f')
                    task["price"] = price

                pic_list = Picture.objects.filter(good_id=item.id)
                if len(pic_list) > 0:
                    pic_url = str(pic_list[0].picture_url)
                if len(pic_list) == 0 or pic_url == "":
                    pic_url = '%s/%s' % (PIC_SAVE_ROOT, "default_image.png")
                if pic_url.startswith("/home/ubuntu"):
                    pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                task["pic_url"] = pic_url
                task["collect_num"] = Collection.objects.filter(good_id=item.id).count()
                task["comment_num"] = Comment.objects.filter(good_id=item.id).count()
                task_list.append(task)
        elif category == 1:
            for item in collections:
                activity_id = item.activity_id
                item = Activity.objects.get(id=activity_id)
                task = {}
                task["task_id"] = item.id
                task["title"] = item.title
                task["category"] = item.category
                task["label"] = item.label
                task["status"] = item.status
                if item.price_req == 1:
                    task["price"] = item.price
                else:
                    task["price"] = "无价位要求"
                pic_list = Picture.objects.filter(activity_id=item.id)
                if len(pic_list) > 0:
                    pic_url = str(pic_list[0].picture_url)
                if len(pic_list) == 0 or pic_url == "":
                    pic_url = '%s/%s' % (PIC_SAVE_ROOT, "default_image.png")

                if pic_url.startswith("/home/ubuntu"):
                    pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                task["pic_url"] = pic_url
                task["collect_num"] = Collection.objects.filter(activity_id=item.id).count()
                task["comment_num"] = Comment.objects.filter(activity_id=item.id).count()
                task_list.append(task)
        response["taskList"] = task_list
        response['msg'] = "success！"
        response['error'] = 0
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
        index = int(request.POST["index"])
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            file = request.FILES.get('pic')
            image_path = '%s/%s%s%s' % (PIC_SAVE_ROOT,
                                        str(int(round(time.time() * 1000))),
                                        str(uuid.uuid1()), file.name)
            image_path = image_path.split(".")[0] + ".png"
            with open(image_path, 'wb') as pic:
                for c in file.chunks():
                    pic.write(c)
            response["pic_url"] = image_path
            response["index"] = index
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
