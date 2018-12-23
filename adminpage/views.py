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
            if status != -1 and status != 0 and status != 1 and status != 2:
                raise InputError("invalid status input")
            category = str(request.POST["category"])
            keyword = str(request.POST["keyword"])
            goods_or_activity = int(request.POST["goods_or_activity"])
            if goods_or_activity != 0 and goods_or_activity != 1:
                raise InputError("invalid goods_or_activity input")
            task_list = Task.objects.filter(goods_or_activity=goods_or_activity)
            if category != "全部":
                task_list = task_list.filter(category=category)
            if status != -1:
                task_list = task_list.filter(status=status)

            task_list = task_list.order_by('-submit_time')

            if keyword != "":
                final_list=[]
                for item in task_list:
                    if item.title.find(keyword) != -1 \
                            or item.detail.find(keyword) != -1 \
                            or item.label.find(keyword) != -1:
                        final_list.append(item)
            else:
                final_list = task_list

            total_num = len(final_list)
            pages = math.ceil(total_num / 10)
            start_num = (page_id - 1) * 10
            if start_num <= total_num and start_num >= 0:
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
                detail = item.detail
                if len(detail) > 15:
                    task["content"] = detail[0:15] + "..."
                else:
                    task["content"] = detail
                if goods_or_activity == 0:
                    price = item.price_for_goods
                    if price == -1:
                        task["price"] = "面议"
                    else:
                        task["price"] = str(price)
                else:
                    task["price"] = item.price_for_activity
                status = item.status
                if status == 0:
                    task["status"] = "待审核"
                elif status == 1:
                    task["status"] = "已上架"
                else:
                    task["status"] = "已下架"

                user_id = item.user_id
                user = User.objects.get(id=user_id)
                task["nickname"] = user.nickname
                contact_info = user.contact_info
                if len(contact_info) > 15:
                    task["user_contact"] = contact_info[0:15] + "..."
                else:
                    task["user_contact"] = contact_info
                return_list.append(task)
            response["data_list"] = return_list
            response["pages"] = pages
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 查看商品详情
@require_http_methods(["POST"])
def get_task_detail(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            task = Task.objects.get(id=int(request.POST["task_id"]))
            response["goods_or_activity"] = task.goods_or_activity
            response["label"] = task.label
            response["category"] = task.category
            response["title"] = task.title
            response["content"] = task.detail
            status = task.status
            if status == 0:
                response["status"] = "待审核"
            elif status == 1:
                response["status"] = "已上架"
            else:
                response["status"] = "已下架"
            if task.goods_or_activity == 0:
                price = task.price_for_goods
                if price == -1:
                    response["price"] = "面议"
                else:
                    response["price"] = str(price)
            else:
                response["price"] = task.price_for_activity
            response["notice"] = task.contact_msg
            response["user_id"] = task.user_id
            user = User.objects.get(id=task.user_id)
            response["nickname"] = user.nickname
            avatar_url = user.avatar_url
            response["avatar_url"] = avatar_url
            response["credit"] = user.credit
            response["user_contact"] = user.contact_info
            # 相关图片
            pic_list = Picture.objects.filter(task_id=task.id)
            pic_url_list = []
            if len(pic_list) > 0:
                for pic in pic_list:
                    pic_url = pic.picture_url
                    if pic_url != "":
                        pic_url_list.append(pic_url)
            else:
                pic_url = '%s/%s' % (PIC_SAVE_ROOT, "default_image.png")
                pic_url = str(SITE_DOMAIN).rstrip("/") + "/showimage" + pic_url
                pic_url_list.append(pic_url)
            response["pics"] = pic_url_list
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 获取十条评论
@require_http_methods(["POST"])
def get_comments(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            page_id = int(request.POST["page"])
            task_id = int(request.POST["task_id"])
            comments = Comment.objects.filter(task_id=task_id)
            total_num = len(comments)
            pages = math.ceil(total_num / 10)
            start_num = (page_id - 1) * 10
            if start_num <= total_num and start_num >= 0:
                end_num = start_num + 10
                if end_num > total_num:
                    end_num = total_num
                comments = comments[start_num:end_num]
            else:
                comments = []
            comment_list = []
            for comment in comments:
                return_comment = {}
                return_comment["comment_id"] = comment.id
                return_comment["reviewer_id"] = comment.reviewer_id
                return_comment["reviewer_nickname"] = User.objects.get(id=comment.reviewer_id).nickname
                return_comment["receiver_id"] = comment.receiver_id
                if comment.receiver_id != -1:
                    return_comment["receiver_nickname"] = User.objects.get(id=comment.receiver_id).nickname
                return_comment["detail"] = comment.detail
                return_comment["time"] = str(comment.release_time.strftime('%Y-%m-%d %H:%M'))
                comment_list.append(return_comment)
            response["comment_list"] = comment_list
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
            task_title = task.title
            status_change = False
            if int(request.POST["agree"]) == 1 and task.status != 1:
                status_change = True
                task.status = 1
                task.release_time = timezone.now()
                task.save()
                title = "您发布的任务已经通过审核"
                detail = '您发布的"' + task_title + '"任务已经通过审核'
            elif int(request.POST["agree"]) == 0 and task.status != 2:
                status_change = True
                task.status = 2
                task.save()
                undercarriage_reason = request.POST["undercarriage_reason"]
                title = "您发布的任务已经下架"
                detail = '您发布的"' + task_title + '"任务已经下架。下架原因：' + undercarriage_reason
            else:
                raise InputError("invalid agree input")

            response['msg'] = "success!"
            response['error'] = 0

            if status_change:
                notification = Notification(receiver_id=task.user_id,
                                            category=0,
                                            comment_id=-1,
                                            relevant_user_id=-1,
                                            task_id=task.id,
                                            title=title,
                                            detail=detail,
                                            user_check=0)
                notification.save()
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
            pre_category = task.category
            if pre_category != request.POST["category"]:
                task.category = request.POST["category"]
                task.save()
                title = "您发布的任务的类型被修改"
                detail = '您发布的"' + task.title + '"任务的类型，从"' + pre_category + '"改为"' + task.category \
                         + '"。请注意您发布消息的类型！'
                notification = Notification(receiver_id=task.user_id,
                                            category=0,
                                            comment_id=-1,
                                            relevant_user_id=-1,
                                            task_id=task.id,
                                            title=title,
                                            detail=detail,
                                            user_check=0)
                notification.save()
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 删除评论，给用户发提醒
@require_http_methods(["POST"])
def delete_comment(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            comment = Comment.objects.get(id=int(request.POST["comment_id"]))
            task = Task.objects.get(id=comment.task_id)
            reason = request.POST["reason"]
            title = "您发布的评论被删除"
            detail = '您在"' + task.title + '"任务下发布的评论"' + comment.detail + '"被删除。删除原因是"' \
                     + reason + '"。请注意您的言辞'
            notification = Notification(receiver_id=comment.reviewer_id,
                                        category=0,
                                        comment_id=-1,
                                        relevant_user_id=-1,
                                        task_id=task.id,
                                        title=title,
                                        detail=detail,
                                        user_check=0)
            comment.delete()
            response['msg'] = "success!"
            response['error'] = 0
            notification.save()
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 获取用户列表
@require_http_methods(["POST"])
def get_user_list(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            page_id = int(request.POST["page"])
            user_id = int(request.POST["user_id"])
            keyword = str(request.POST["keyword"])
            user_list = []
            if user_id != -1:
                user = User.objects.get(id=user_id)
                user_list.append(user)
                pages = 1
            else:
                all_user_list = User.objects.all()
                if keyword != "":
                    for user in all_user_list:
                        if user.nickname.find(keyword) != -1:
                            user_list.append(user)
                else:
                    user_list = all_user_list

                total_num = len(user_list)
                pages = math.ceil(total_num / 10)
                start_num = (page_id - 1) * 10
                if start_num <= total_num and start_num >= 0:
                    end_num = start_num + 10
                    if end_num > total_num:
                        end_num = total_num
                    user_list = user_list[start_num:end_num]
                else:
                    user_list = []

            return_list = []
            for user in user_list:
                info = {}
                info["user_id"] = user.id
                info["nickname"] = user.nickname
                info["user_contact"] = user.contact_info
                avatar_url = user.avatar_url
                info["avatar_url"] = avatar_url
                info["credit"] = user.credit
                info["task_num"] = Task.objects.filter(user_id=user.id).count()
                info["comment_num"] = Comment.objects.filter(reviewer_id=user.id).count()
                info["collect_num"] = Collection.objects.filter(user_id=user.id).count()
                return_list.append(info)
            response["user_list"] = return_list
            response["pages"] = pages
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 获取用户信息
@require_http_methods(["POST"])
def get_user_detail(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            user_id = int(request.POST["user_id"])
            user = User.objects.get(id=user_id)
            response["user_id"] = user.id
            response["nickname"] = user.nickname
            response["user_contact"] = user.contact_info
            avatar_url = user.avatar_url
            response["avatar_url"] = avatar_url
            response["credit"] = user.credit
            response["task_num"] = Task.objects.filter(user_id=user.id).count()
            response["comment_num"] = Comment.objects.filter(reviewer_id=user.id).count()
            response["collect_num"] = Collection.objects.filter(user_id=user.id).count()
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 给用户发消息
@require_http_methods(["POST"])
def send_message(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            user_id = int(request.POST["user_id"])
            if User.objects.filter(id=user_id).count() <= 0:
                raise InputError("invalid user id input")
            detail = str(request.POST["detail"])
            relevant_task_id = int(request.POST["relevant_task_id"])
            if relevant_task_id != -1 and Task.objects.filter(id=relevant_task_id).count() <= 0:
                raise InputError("invalid task id input")
            notification = Notification(receiver_id=user_id,
                                        category=0,
                                        comment_id=-1,
                                        relevant_user_id=-1,
                                        task_id=relevant_task_id,
                                        title="管理员给您发消息",
                                        detail=detail,
                                        user_check=0)
            notification.save()
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 获取历史任务
@require_http_methods(["POST"])
def get_history_tasks(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            user_id = int(request.POST["user_id"])
            page_id = int(request.POST["page"])
            if User.objects.filter(id=user_id).count() <= 0:
                raise InputError("invalid user id")
            task_list = Task.objects.filter(user_id=user_id).order_by("-submit_time")
            total_num = len(task_list)
            pages = math.ceil(total_num / 10)
            start_num = (page_id - 1) * 10
            if start_num <= total_num and start_num >= 0:
                end_num = start_num + 10
                if end_num > total_num:
                    end_num = total_num
                task_list = task_list[start_num:end_num]
            else:
                task_list = []
            return_list = []
            for item in task_list:
                task = {}
                task["task_id"] = item.id
                task["label"] = item.label
                task["category"] = item.category
                task["title"] = item.title
                detail = item.detail
                if len(detail) > 15:
                    task["content"] = detail[0:15] + "..."
                else:
                    task["content"] = detail
                if item.goods_or_activity == 0:
                    price = item.price_for_goods
                    if price == -1:
                        task["price"] = "面议"
                    else:
                        task["price"] = str(price)
                else:
                    task["price"] = item.price_for_activity
                status = item.status
                if status == 0:
                    task["status"] = "待审核"
                elif status == 1:
                    task["status"] = "已上架"
                else:
                    task["status"] = "已下架"
                release_time = str(item.submit_time.strftime('%Y-%m-%d %H:%M'))
                task["time"] = release_time
                return_list.append(task)
            response["data_list"] = return_list
            response["pages"] = pages
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 获取历史评论
@require_http_methods(["POST"])
def get_history_comments(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            user_id = int(request.POST["user_id"])
            page_id = int(request.POST["page"])
            if User.objects.filter(id=user_id).count() <= 0:
                raise InputError("invalid user id")
            comment_list = Comment.objects.filter(reviewer_id=user_id).order_by("-release_time")
            total_num = len(comment_list)
            pages = math.ceil(total_num / 10)
            start_num = (page_id - 1) * 10
            if start_num <= total_num and start_num >= 0:
                end_num = start_num + 10
                if end_num > total_num:
                    end_num = total_num
                comment_list = comment_list[start_num:end_num]
            else:
                comment_list = []
            return_list = []
            for item in comment_list:
                comment_info = {}
                comment_info["comment_id"] = item.id
                comment_info["task_id"] = item.task_id
                comment_info["task_title"] = Task.objects.get(id=item.task_id).title
                comment_info["receiver_id"] = item.receiver_id
                if User.objects.filter(id=item.receiver_id).count() > 0:
                    comment_info["receiver_nickname"] = User.objects.get(id=item.receiver_id).nickname
                comment_info["detail"] = item.detail
                comment_info["time"] = str(item.release_time.strftime('%Y-%m-%d %H:%M'))
                return_list.append(comment_info)
            response["comment_list"] = return_list
            response["pages"] = pages
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 查看用户反馈
@require_http_methods(["POST"])
def get_user_feedback(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            type = int(request.POST["type"])
            page_id = int(request.POST["page"])

            if type != -1 and type != 0 and type != 1:
                raise InputError("type input should be -1 or 0 or 1")
            feedback_list = Feedback.objects.all()
            if type != -1:
                feedback_list = feedback_list.filter(admin_check=type)
            total_num = len(feedback_list)
            pages = math.ceil(total_num / 10)
            start_num = (page_id - 1) * 10
            if start_num <= total_num and start_num >= 0:
                end_num = start_num + 10
                if end_num > total_num:
                    end_num = total_num
                    feedback_list = feedback_list[start_num:end_num]
            else:
                feedback_list = []
            return_list = []
            for feedback in feedback_list:
                info = {}
                info["feedback_id"] = feedback.id
                info["detail"] = feedback.detail
                info["user_id"] = feedback.user_id
                user = User.objects.get(id=feedback.user_id)
                info["user_contact"] = user.contact_info
                info["nickname"] = user.nickname
                info["time"] = str(feedback.release_time.strftime('%Y-%m-%d %H:%M'))
                # 相关图片
                pic_list = Picture.objects.filter(feedback_id=feedback.id)
                pic_url_list = []
                if len(pic_list) > 0:
                    for pic in pic_list:
                        pic_url = pic.picture_url
                        if pic_url != "":
                            pic_url_list.append(pic_url)
                info["pics"] = pic_url_list
                return_list.append(info)
            response["pages"] = pages
            response["feedback_list"] = return_list
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response


# 反馈已查看
@require_http_methods(["POST"])
def admin_check_feedback(request):
    response = {}
    try:
        if not request.user.is_authenticated:
            raise ValidateError("admin-user not login!")
        else:
            feedback_id = int(request.POST["feedback_id"])
            feedback = Feedback.objects.get(id=feedback_id)
            feedback.admin_check = 1
            feedback.save()
            response['msg'] = "success!"
            response['error'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error'] = 1
    finally:
        response = JsonResponse(response)
        return response
