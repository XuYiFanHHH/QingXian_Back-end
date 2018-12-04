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
from django.db.models import Q


# 查看skey是否有效
@require_http_methods(["POST"])
def check_skey(request):
    response = {}
    try:
        skey = request.POST["skey"]
        length = User.objects.filter(skey=skey).count()
        if length > 0:
            response['valid'] = 1
        else:
            response['valid'] = 0
        response['msg'] = "success"
        response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
        response['valid'] = 0
    finally:
        response = JsonResponse(response)
        return response

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
            obj = User(open_id=openid, skey=skey, credit=100, nickname="", contact_info="")
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
def insert_user(request):
    response = {}
    try:
        skey = request.POST["skey"]
        result_list = User.objects.filter(skey=skey)

        if len(result_list) > 0:
            result_list[0].nickname = request.POST['nickname']
            result_list[0].avatar_url = request.POST['avatar_url']
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


# 返回用户信用分,用户信息,头像图片
@require_http_methods(["POST"])
def get_user_info(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        response['credit'] = user.credit
        response['nickname'] = user.nickname
        avatar_url = user.avatar_url
        if avatar_url.startswith("/home/"):
            avatar_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + avatar_url
        response["avatar_url"] = avatar_url
        response["user_contact"] = user.contact_info
        response['msg'] = "success!"
        response['error'] = 0
    except Exception as e:
        response['credit'] = -1
        response['nickname'] = ""
        response["avatar_url"] = ""
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 更新用户信息
@require_http_methods(["POST"])
def update_user_info(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        user.nickname = request.POST["nickname"]
        user.avatar_url = request.POST["avatar_url"]
        user.contact_info = request.POST["user_contact"]
        user.save()
        response['msg'] = "success"
        response['error'] = 0
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
        user = User.objects.get(skey=skey)
        user_id = user.id
        detail = request.POST["detail"]
        feedback = Feedback(user_id=user_id, detail=detail)
        feedback.save()

        split_list = request.POST["pics"].split(",")
        pic_list = []
        for pic in split_list:
            if pic:
                pic_list.append(pic)
        for pic in pic_list:
            picture = Picture(picture_url=pic,
                              task_id=-1,
                              feedback_id=feedback.id
                              )
            picture.save()
        response['msg'] = "success"
        response['error'] = 0
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
        # 按照user_id和status来筛选，并按提交时间倒排
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        status = int(request.POST["status"])
        page_id = int(request.POST["page"])
        task_list = []
        all_task = Task.objects.filter(user_id=user.id)
        if status == 0 or status == 1 or status == 2:
            all_task = all_task.filter(status=status)
        else:
            raise InputError("invalid status input")
        all_task = all_task.order_by("-submit_time")
        # 按照页数，取某几条数据
        total_num = len(all_task)
        start_num = (page_id - 1) * 10
        if start_num <= total_num and start_num >= 0:
            end_num = start_num + 10
            if end_num > total_num:
                end_num = total_num
            all_task = all_task[start_num:end_num]
        else:
            all_task = []

        for item in all_task:
            task = {}
            task["task_id"] = item.id
            task["goods_or_activity"] = item.goods_or_activity
            task["title"] = item.title
            task["category"] = item.category
            task["label"] = item.label
            # 取第一张图片
            pic_list = Picture.objects.filter(task_id=item.id)
            if len(pic_list) > 0:
                pic_url = str(pic_list[0].picture_url)
            if len(pic_list) == 0 or pic_url == "":
                pic_url = '%s/%s' % (PIC_SAVE_ROOT, "default_image.png")
            if pic_url.startswith("/home/ubuntu"):
                pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
            task["pic"] = pic_url
            task["collect_num"] = Collection.objects.filter(task_id=item.id).count()
            task["comment_num"] = Comment.objects.filter(task_id=item.id).count()

            if item.goods_or_activity == 0:
                price = int(item.price_for_goods)
                if price == -1:
                    task["price"] = "面议"
                else:
                    task["price"] = str(price)
            else:
                price = item.price_for_activity
                if price:
                    task["price"] = price
                else:
                    task["price"] = "无价位要求"
            task_list.append(task)

        response["task_list"] = task_list
        response['msg'] = "success"
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
        goods_or_activity = int(request.POST["goods_or_activity"])
        if goods_or_activity != 0 and goods_or_activity != 1:
            raise InputError("goods_or_activity input error")
        page_id = int(request.POST["page"])
        collections = Collection.objects.filter(user_id=user.id).order_by("-collect_time")
        collect_list = []
        for collection in collections:
            task = Task.objects.get(id=collection.task_id)
            if task.goods_or_activity == goods_or_activity:
                collect_list.append(task)

        total_num = len(collect_list)
        start_num = (page_id - 1) * 10
        if start_num <= total_num and start_num >= 0:
            end_num = start_num + 10
            if end_num > total_num:
                end_num = total_num
            collect_list = collect_list[start_num:end_num]
        else:
            collect_list = []

        task_list = []
        for item in collect_list:
            task = {}
            task["task_id"] = item.id
            task["title"] = item.title
            task["category"] = item.category
            task["label"] = item.label
            task["status"] = item.status
            # 取第一张图片
            pic_list = Picture.objects.filter(task_id=item.id)
            if len(pic_list) > 0:
                pic_url = str(pic_list[0].picture_url)
            if len(pic_list) == 0 or pic_url == "":
                pic_url = '%s/%s' % (PIC_SAVE_ROOT, "default_image.png")
            if pic_url.startswith("/home/ubuntu"):
                pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
            task["pic"] = pic_url
            task["collect_num"] = Collection.objects.filter(task_id=item.id).count()
            task["comment_num"] = Comment.objects.filter(task_id=item.id).count()

            if item.goods_or_activity == 0:
                price = int(item.price_for_goods)
                if price == -1:
                    task["price"] = "面议"
                else:
                    task["price"] = str(price)
            else:
                price = item.price_for_activity
                if price:
                    task["price"] = price
                else:
                    task["price"] = "无价位要求"
            task_list.append(task)
        response["task_list"] = task_list
        response['msg'] = "success"
        response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 添加任务
@require_http_methods(["POST"])
def add_new_task(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        user_id = user.id
        user_credit = user.credit
        label = str(request.POST["label"])
        category = str(request.POST["category"])
        title = str(request.POST["title"])
        detail = str(request.POST["detail"])
        contact_msg = str(request.POST["notice"])
        price = request.POST["price"]

        goods_or_activity = int(request.POST["goods_or_activity"])
        if goods_or_activity != 0 and goods_or_activity != 1:
            raise InputError("goods_or_activity input error")
        if goods_or_activity == 0:
            price_for_goods = int(price)
            price_for_activity = ""
        else:
            price_for_goods = -1
            price_for_activity = str(price)

        new_task = Task(user_id=user_id,
                        user_credit=user_credit,
                        goods_or_activity = goods_or_activity,
                        label=label,
                        title=title,
                        detail=detail,
                        category=category,
                        price_for_goods=price_for_goods,
                        price_for_activity=price_for_activity,
                        contact_msg=contact_msg,
                        status=0)
        new_task.save()

        # 保存相关图片
        split_list = request.POST["pics"].split(",")
        pic_list = []
        for pic in split_list:
            if pic:
                pic_list.append(pic)
        for pic in pic_list:
            picture = Picture(picture_url=pic,
                              task_id=new_task.id,
                              feedback_id=-1
                              )
            picture.save()
        response['msg'] = "success"
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


# 获取已上架任务总数
@require_http_methods(["POST"])
def get_valid_task_number(request):
    response = {}
    try:
        skey = request.POST["skey"]
        goods_or_activity = int(request.POST["goods_or_activity"])
        if goods_or_activity != 0 and goods_or_activity != 1:
            raise InputError("goods_or_activity input error")
        user_list = User.objects.filter(skey=skey)
        if len(user_list) > 0:
            response["number"] = Task.objects.filter(status=1).\
                filter(goods_or_activity=goods_or_activity).count()
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


# 根据页数和相关参数获取某一些任务
@require_http_methods(["POST"])
def get_tasks(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        user_id = user.id
        page_id = int(request.POST["page"])
        goods_or_activity = int(request.POST["goods_or_activity"])
        if goods_or_activity != 0 and goods_or_activity != 1:
            raise InputError("goods_or_activity input error")
        select_index = int(request.POST["select_index"])
        sort_index = int(request.POST["sort_index"])
        category = str(request.POST["category"])
        keyword = str(request.POST["keyword"])

        # 从已上架的商品中筛选
        task_list = Task.objects.filter(status=1, goods_or_activity=goods_or_activity)

        if select_index == 1:
            if goods_or_activity == 0:
                task_list = task_list.filter(label="出售")
            elif goods_or_activity == 1:
                task_list = task_list.filter(~Q(price_for_activity=""))
        elif select_index == 2:
            if goods_or_activity == 0:
                task_list = task_list.filter(label="求购")
            elif goods_or_activity == 1:
                task_list = task_list.filter(price_for_activity="")
        elif select_index != 0:
            raise InputError("select_index input error")

        # 排序
        if sort_index == 0:
            task_list = task_list.order_by('-submit_time')
        elif sort_index == 1:
            task_list = task_list.order_by('submit_time')
        elif sort_index == 2 and goods_or_activity == 0:
            task_list = task_list.order_by('-price_for_goods')
        elif sort_index == 2 and goods_or_activity == 1:
            task_list = task_list.order_by('-user_credit')
        elif sort_index == 3 and goods_or_activity == 0:
            task_list = task_list.order_by('price_for_goods')
        elif sort_index == 4 and goods_or_activity == 0:
            task_list = task_list.order_by('-user_credit')
        else:
            raise InputError("sort_index input error")

        if keyword:
            final_list = []
            for item in task_list:
                if item.title.find(keyword) != -1 \
                        or item.detail.find(keyword) != -1\
                        or item.label.find(keyword) != -1:
                    final_list.append(item)
        else:
            if category != "全部":
                final_list = task_list.filter(category=category)
            else:
                final_list = task_list


        total_num = len(final_list)
        start_num = (page_id - 1) * 10
        if start_num <= total_num and start_num >= 0:
            end_num = start_num + 10
            if end_num > total_num:
                end_num = total_num
            final_list = final_list[start_num:end_num]
        else:
            final_list = []
        return_list = []
        for item in final_list:
            task = {}
            task["task_id"] = item.id
            task["label"] = item.label
            task["title"] = item.title
            task["detail"] = item.detail

            if item.goods_or_activity == 0:
                price = int(item.price_for_goods)
                if price == -1:
                    task["price"] = "面议"
                else:
                    task["price"] = str(price)
            else:
                price = item.price_for_activity
                if price:
                    task["price"] = price
                else:
                    task["price"] = "无价位要求"

            task["user_id"] = item.user_id
            task["user_credit"] = item.user_credit
            publisher = User.objects.get(id=item.user_id)
            task["user_nickname"] = publisher.nickname
            avatar_url = publisher.avatar_url
            if avatar_url.startswith("/home/"):
                avatar_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + avatar_url
            task["user_avatar"] = avatar_url
            # 第一张相关图片
            pic_list = Picture.objects.filter(task_id=item.id).order_by("id")
            pic_url_list = []
            if len(pic_list) > 0:
                for pic in pic_list:
                    pic_url = pic.picture_url
                    if pic_url.startswith("/home/ubuntu"):
                        pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                    if pic_url != "":
                        pic_url_list.append(pic_url)
            task["pics"] = pic_url_list
            if len(pic_url_list) > 0:
                task["pic"] = pic_url_list[0]
            else:
                pic_url = '%s/%s' % (PIC_SAVE_ROOT, "default_image.png")
                task["pic"] = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url

            task["collect_num"] = Collection.objects.filter(task_id=item.id).count()
            task["comment_num"] = Comment.objects.filter(task_id=item.id).count()
            # 相关评论
            comment_list = []
            comments = Comment.objects.filter(task_id=item.id)
            for comment in comments:
                return_comment = {}
                return_comment["reviewer_id"] = comment.reviewer_id
                return_comment["reviewer_nickname"] = User.objects.get(id=comment.reviewer_id).nickname
                return_comment["receiver_id"] = comment.receiver_id
                if comment.receiver_id != -1:
                    return_comment["receiver_nickname"] = User.objects.get(id=comment.receiver_id).nickname
                return_comment["detail"] = comment.detail
                return_comment["time"] = str(comment.release_time.strftime('%Y-%m-%d %H:%M'))
                comment_list.append(return_comment)
            task["comment_list"] = comment_list

            select_result = Collection.objects.filter(user_id=user_id, task_id=item.id)
            if len(select_result) > 0:
                task["hasCollect"] = 1
            else:
                task["hasCollect"] = 0
            # 计算提交时间
            release_time = str(item.submit_time.strftime('%Y-%m-%d %H:%M'))
            un_time = time.mktime(item.submit_time.timetuple())
            task["submit_time_count"] = un_time
            task["submit_time"] = release_time
            return_list.append(task)
        response["data_list"] = return_list
        response["msg"] = "success"
        response["error"] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 任务查看详情
@require_http_methods(["POST"])
def get_task_detail(request):
    response = {}
    try:
        skey = str(request.POST["skey"])
        task_id = int(request.POST["task_id"])
        user = User.objects.get(skey=skey)
        user_id = user.id
        task = Task.objects.get(id=task_id)
        response["task_id"] = task.id
        response["title"] = task.title
        response["detail"] = task.detail
        if task.goods_or_activity == 0:
            price = int(task.price_for_goods)
            if price == -1:
                response["price"] = "面议"
            else:
                response["price"] = str(price)
        else:
            price = task.price_for_activity
            if price:
                response["price"] = price
            else:
                response["price"] = "无价位要求"
        response["notice"] = task.contact_msg

        publisher = User.objects.get(id=task.user_id)
        response["user_credit"] = publisher.credit
        response["nickname"] = publisher.nickname
        avatar_url = str(publisher.avatar_url)
        if avatar_url.startswith("/home/"):
            avatar_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + avatar_url
        response["avatar"] = avatar_url
        # 任务相关图片
        pic_list = Picture.objects.filter(task_id=task_id)
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
        response["pics"] = pic_url_list

        # 相关评论
        comment_list = []
        comments = Comment.objects.filter(task_id=task_id)
        for comment in comments:
            return_comment = {}
            return_comment["reviewer_id"] = comment.reviewer_id
            return_comment["reviewer_nickname"] = User.objects.get(id=comment.reviewer_id).nickname
            return_comment["receiver_id"] = comment.receiver_id
            if comment.receiver_id != -1:
                return_comment["receiver_nickname"] = User.objects.get(id=comment.receiver_id).nickname
            return_comment["detail"] = comment.detail
            return_comment["time"] = str(comment.release_time.strftime('%Y-%m-%d %H:%M'))
            comment_list.append(return_comment)
        
        response["comment_list"] = comment_list

        select_result = Collection.objects.filter(user_id=user_id, task_id=task.id)
        if len(select_result) > 0:
            response["hasCollect"] = 1
        else:
            response["hasCollect"] = 0
        # 计算提交时间
        release_time = str(task.submit_time.strftime('%Y-%m-%d %H:%M'))
        un_time = time.mktime(task.submit_time.timetuple())
        response["submit_time_count"] = un_time
        response["submit_time"] = release_time
        response["msg"] = "success"
        response["error"] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 获取发布者联系信息
@require_http_methods(["POST"])
def get_publisher_contact(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        task = Task.objects.get(id=request.POST["task_id"])
        publisher = User.objects.get(id=task.user_id)
        if user.contact_info == "":
            response['msg'] = "请先填写您自己的联系方式！"
            response['error'] = 2
        else:
            if task.user_id == user.id:
                raise LogicError("你想获取自己的联系方式？？")
            response["user_contact"] = publisher.contact_info
            response["notice"] = task.contact_msg
            response['msg'] = "success"
            response['error'] = 0
            title = user.nickname + " 获取了你的联系方式"
            notification = Notification(receiver_id=task.user_id,
                                        category=1,
                                        comment_id=-1,
                                        relevant_user_id=user.id,
                                        task_id=task.id,
                                        title=title,
                                        detail="",
                                        user_check=0)
            notification.save()
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 二手商品收藏与取消收藏
@require_http_methods(["POST"])
def task_collection_changed(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        user_id = user.id
        task_id = int(request.POST["task_id"])
        collect_id = int(request.POST["collect_id"])
        if Task.objects.filter(id=task_id).count() <= 0:
            raise InputError("invalid task id")
        collect_result = Collection.objects.filter(user_id=user_id, task_id=task_id)
        if len(collect_result) > 0:
            collect_result.delete()
            response["hasCollect"] = 0
        else:
            collection = Collection(user_id=user_id,
                                    task_id=task_id,
                                    )
            collection.save()
            response["hasCollect"] = 1
        response["collect_id"] = collect_id
        response["msg"] = "success"
        response["error"] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 任务添加评论
@require_http_methods(["POST"])
def add_comment(request):
    response = {}
    try:
        skey = request.POST["skey"]
        user = User.objects.get(skey=skey)
        user_id = user.id
        task_id = int(request.POST["task_id"])
        receiver_id = int(request.POST["receiver_id"])
        detail = str(request.POST["detail"])
        comment = Comment(reviewer_id=user_id,
                          receiver_id=receiver_id,
                          detail=detail,
                          task_id=task_id,
                          )
        comment.save()
        task = Task.objects.get(id=task_id)
        # 对该任务的评论，则发消息给发布者
        if receiver_id == -1:
            title = user.nickname + " 评论了你的发布任务"
            notification = Notification(receiver_id=task.user_id,
                                        category=1,
                                        comment_id=comment.id,
                                        relevant_user_id=user_id,
                                        task_id=task_id,
                                        title=title,
                                        detail=detail,
                                        user_check=0)
            notification.save()
        # 是对某人评论的回复，则发消息给该用户
        else:
            title = user.nickname + " 回复了你的评论"
            notification = Notification(receiver_id=receiver_id,
                                        category=1,
                                        comment_id=comment.id,
                                        relevant_user_id=user_id,
                                        task_id=task_id,
                                        title=title,
                                        detail=detail,
                                        user_check=0)
            notification.save()
        response["msg"] = "success"
        response["error"] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 提醒界面初始化
@require_http_methods(["POST"])
def get_notifications(request):
    response = {}
    try:
        skey = request.POST["skey"]
        page_id = int(request.POST["page"])
        user = User.objects.get(skey=skey)
        notification_list = Notification.objects.filter(receiver_id=user.id)
        # 未读的系统消息
        system_notice_count = notification_list.filter(category=0, user_check=0).count()
        # 用户消息按时间倒排
        notification_list = notification_list.filter(category=1).order_by("-release_time")
        total_num = len(notification_list)
        start_num = (page_id - 1) * 10
        if start_num <= total_num and start_num >= 0:
            end_num = start_num + 10
            if end_num > total_num:
                end_num = total_num
            notification_list = notification_list[start_num:end_num]
        else:
            notification_list = []
        user_notice_list=[]
        for notice in notification_list:
            message = {}
            task = Task.objects.get(id=notice.task_id)
            relevant_user = User.objects.get(id=notice.relevant_user_id)
            message["task_id"] = notice.task_id
            message["title"] = notice.title
            message["task_title"] = task.title
            content = notice.detail
            if len(content) > 25:
                content = content[0:25] + "..."
            message["content"] = content
            avatar_url = str(relevant_user.avatar_url)
            if avatar_url.startswith("/home/"):
                avatar_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + avatar_url
            message["user_avatar_url"] = avatar_url
            # 第一张任务相关图片
            pic_list = Picture.objects.filter(task_id=task.id).order_by("id")
            if len(pic_list) > 0:
                pic_url = str(pic_list[0].picture_url)
            if len(pic_list) == 0 or pic_url == "":
                pic_url = ""
            if pic_url.startswith("/home/ubuntu"):
                pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
            message["task_image_url"] = pic_url
            # 计算提醒发送时间
            release_time = str(notice.release_time.strftime('%Y-%m-%d %H:%M'))
            un_time = time.mktime(notice.release_time.timetuple())
            message["time_count"] = un_time
            message["time"] = release_time
            user_notice_list.append(message)
            # 用户查阅过
            notice.user_check = 1
            notice.save()
        response["system_notice_count"] = system_notice_count
        response["user_notice_list"] = user_notice_list
        response['msg'] = "success!"
        response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 系统提醒消息
@require_http_methods(["POST"])
def get_system_notifications(request):
    response = {}
    try:
        skey = request.POST["skey"]
        page_id = int(request.POST["page"])
        user = User.objects.get(skey=skey)
        # 系统消息按时间倒排
        notification_list = Notification.objects.\
            filter(receiver_id=user.id, category=0).order_by("-release_time")
        total_num = len(notification_list)
        start_num = (page_id - 1) * 10
        if start_num <= total_num and start_num >= 0:
            end_num = start_num + 10
            if end_num > total_num:
                end_num = total_num
            notification_list = notification_list[start_num:end_num]
        else:
            notification_list = []
        system_notice_list=[]
        for notice in notification_list:
            message = {}
            message["task_id"] = notice.task_id
            message["title"] = notice.title
            message["content"] = notice.detail
            # 计算提醒发送时间
            release_time = str(notice.release_time.strftime('%Y-%m-%d %H:%M'))
            un_time = time.mktime(notice.release_time.timetuple())
            message["time_count"] = un_time
            message["time"] = release_time
            system_notice_list.append(message)
            # 用户查阅过
            notice.user_check = 1
            notice.save()
        response["notice_list"] = system_notice_list
        response['msg'] = "success!"
        response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response