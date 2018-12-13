from django.test import TestCase
from django.contrib.auth.models import User
from wechat.models import Task, Picture, Comment, Feedback, Collection, Notification
from QingXian.settings import *
from wechat.models import User as WechatUser
import json


# 测试 管理员登录
class AdminLoginTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")
        self.request_url = "/adminpage/login"

    # 正确输入测试
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

    # 测试username
    def test_invalid_username_request(self):
        request_dict = {"username": "admi",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"password": "adminpass"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试password
    def test_invalid_password_request(self):
        request_dict = {"username": "admin",
                        "password": "admin"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"username": "admin"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试 管理员登出
class AdminLogoutTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")
        self.request_url = "/adminpage/logout"

    # 正确输入测试
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        response_json = json.loads(self.client.post(self.request_url, {}).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

    # 测试未登录时候登出
    def test_error_request(self):
        response_json = json.loads(self.client.post(self.request_url, {}).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试获取所有任务信息
class GetAllTaskTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")

        user = WechatUser.objects.create(open_id="111",
                                         skey="111",
                                         nickname="1",
                                         contact_info="18800123333",
                                         avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")

        user2 = WechatUser.objects.create(open_id="222",
                                          skey="222",
                                          nickname="2",
                                          contact_info="哈哈哈哈我的手机号码是！！！！！：：：：18800123333",
                                          avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")

        task4 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="出售",
                                    category="学习",
                                    title="出售笔记本电脑",
                                    detail="出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        task3 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="求购",
                                    category="学习",
                                    title="求购笔记本电脑",
                                    detail="求购苹果电脑",
                                    price_for_goods=-1,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=1)

        task2 = Task.objects.create(user_id=user2.id,
                                    user_credit=100,
                                    goods_or_activity=1,
                                    label="休闲娱乐",
                                    category="休闲娱乐",
                                    title="一起买笔记本电脑",
                                    detail="找朋友一起笔记本电脑",
                                    price_for_goods=-1,
                                    price_for_activity="不高于59元/场",
                                    contact_msg="请加我的微信",
                                    status=2)

        task1 = Task.objects.create(user_id=user2.id,
                                    user_credit=100,
                                    goods_or_activity=1,
                                    label="失物招领",
                                    category="失物招领",
                                    title="捡到笔记本",
                                    detail="捡到笔记本电脑",
                                    price_for_goods=-1,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        self.request_url = "/adminpage/task/get_all"

    # 测试goods_or_activity参数
    def test_goods_or_activity_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        request_dict = {"goods_or_activity": 0,
                        "status": -1,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 2)
        task0 = data_list[0]
        task1 = data_list[1]
        self.assertEqual(task0["label"], "求购")
        self.assertEqual(task0["category"], "学习")
        self.assertEqual(task0["title"], "求购笔记本电脑")
        self.assertEqual(task0["price"], "面议")
        self.assertEqual(task0["content"], "求购苹果电脑")
        self.assertEqual(task0["status"], "已上架")
        self.assertEqual(task0["nickname"], "1")
        self.assertEqual(task0["user_contact"], "18800123333")

        self.assertEqual(task1["price"], "8000")
        self.assertLessEqual(len(task1["content"]), 18)
        if str(task1["content"]).endswith("..."):
            right = 1
        else:
            right = 0
        self.assertEqual(right, 1)
        self.assertEqual(task1["status"], "待审核")

        # 消息活动
        request_dict = {"goods_or_activity": 1,
                        "status": -1,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 2)
        task0 = data_list[0]
        task1 = data_list[1]
        self.assertLessEqual(task0["price"], "")
        self.assertLessEqual(task1["price"], "不高于59元/场")
        self.assertEqual(task0["status"], "待审核")
        self.assertEqual(task1["status"], "已下架")

        self.assertLessEqual(len(task1["user_contact"]), 18)
        if str(task1["user_contact"]).endswith("..."):
            right = 1
        else:
            right = 0
        self.assertEqual(right, 1)

        # 无效的goods_or_activity
        request_dict = {"goods_or_activity": -1,
                        "status": -1,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"goods_or_activity": 2,
                        "status": -1,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试status参数
    def test_status_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        # status为0
        request_dict = {"goods_or_activity": 1,
                        "status": 0,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 1)
        task0 = data_list[0]
        self.assertEqual(task0["label"], "失物招领")

        request_dict = {"goods_or_activity": 0,
                        "status": 0,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 1)
        task0 = data_list[0]
        self.assertEqual(task0["label"], "出售")

        # status为1
        request_dict = {"goods_or_activity": 0,
                        "status": 1,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 1)
        task0 = data_list[0]
        self.assertLessEqual(task0["label"], "求购")

        request_dict = {"goods_or_activity": 1,
                        "status": 1,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 0)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 0)

        # status为2
        request_dict = {"goods_or_activity": 0,
                        "status": 2,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 0)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 0)

        request_dict = {"goods_or_activity": 1,
                        "status": 2,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 1)
        task0 = data_list[0]
        self.assertLessEqual(task0["label"], "休闲娱乐")

        # 无效的status
        request_dict = {"goods_or_activity": 1,
                        "status": -2,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"goods_or_activity": 1,
                        "status": 3,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试category参数
    def test_category_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        # category有效
        request_dict = {"goods_or_activity": 0,
                        "status": -1,
                        "category": "学习",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 2)
        task0 = data_list[0]
        task1 = data_list[1]
        self.assertEqual(task0["label"], "求购")
        self.assertEqual(task1["label"], "出售")

        # category无效
        request_dict = {"goods_or_activity": 1,
                        "status": -1,
                        "category": "学习",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 0)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 0)

    # 测试keyword参数
    def test_keyword_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        # keyword
        request_dict = {"goods_or_activity": 0,
                        "status": -1,
                        "category": "全部",
                        "keyword": "电脑",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 2)
        task0 = data_list[0]
        task1 = data_list[1]
        self.assertEqual(task0["label"], "求购")
        self.assertEqual(task1["label"], "出售")

        # keyword + category
        request_dict = {"goods_or_activity": 1,
                        "status": -1,
                        "category": "休闲娱乐",
                        "keyword": "电脑",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 1)
        task0 = data_list[0]
        self.assertEqual(task0["label"], "休闲娱乐")

        # 无效keyword
        request_dict = {"goods_or_activity": 1,
                        "status": -1,
                        "category": "休闲娱乐",
                        "keyword": "失物",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 0)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 0)

        request_dict = {"goods_or_activity": 1,
                        "status": -1,
                        "category": "全部",
                        "keyword": "电影",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 0)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 0)

    # 测试page参数
    def test_invalid_page_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        request_dict = {"goods_or_activity": 0,
                        "status": -1,
                        "category": "全部",
                        "keyword": "",
                        "page": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 0)

        request_dict = {"goods_or_activity": 0,
                        "status": -1,
                        "category": "全部",
                        "keyword": "",
                        "page": 2}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 0)

    # 测试未登录
    def test_error_request(self):
        request_dict = {"goods_or_activity": 0,
                        "status": -1,
                        "category": "全部",
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试获取任务信息详情
class GetTaskDetailTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")

        user = WechatUser.objects.create(open_id="111",
                                         skey="111",
                                         nickname="1",
                                         contact_info="18800123333",
                                         avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image1.png")

        user2 = WechatUser.objects.create(open_id="222",
                                          skey="222",
                                          nickname="2",
                                          contact_info="哈哈哈哈我的手机号码是！！！！！：：：：18800123333",
                                          avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image2.png")

        task1 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="出售",
                                    category="学习",
                                    title="出售笔记本电脑",
                                    detail="出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        task2 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="求购",
                                    category="学习",
                                    title="求购笔记本电脑",
                                    detail="求购苹果电脑",
                                    price_for_goods=-1,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=1)

        Picture.objects.create(picture_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/test.png",
                               task_id=task2.id,
                               feedback_id=-1)

        task3 = Task.objects.create(user_id=user2.id,
                                    user_credit=100,
                                    goods_or_activity=1,
                                    label="休闲娱乐",
                                    category="休闲娱乐",
                                    title="一起买笔记本电脑",
                                    detail="找朋友一起笔记本电脑",
                                    price_for_goods=-1,
                                    price_for_activity="不高于59元/场",
                                    contact_msg="请加我的微信",
                                    status=2)

        task4 = Task.objects.create(user_id=user2.id,
                                    user_credit=100,
                                    goods_or_activity=1,
                                    label="失物招领",
                                    category="失物招领",
                                    title="捡到笔记本",
                                    detail="捡到笔记本电脑",
                                    price_for_goods=-1,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        self.request_url = "/adminpage/task/get_task_detail"

    # 测试不同的task_id
    def test_different_task_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        task1 = Task.objects.get(label="出售")
        task2 = Task.objects.get(label="求购")
        task3 = Task.objects.get(label="休闲娱乐")
        task4 = Task.objects.get(label="失物招领")

        request_dict = {"task_id": task1.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        goods_or_activity = response_json['goods_or_activity']
        label = response_json['label']
        category = response_json['category']
        title = response_json['title']
        content = response_json['content']
        price = response_json['price']
        status = response_json['status']
        notice = response_json['notice']
        nickname = response_json['nickname']
        avatar_url = response_json['avatar_url']
        credit = response_json['credit']
        user_contact = response_json['user_contact']
        pics = response_json['pics']
        self.assertEqual(goods_or_activity, 0)
        self.assertEqual(label, "出售")
        self.assertEqual(category, "学习")
        self.assertEqual(title, "出售笔记本电脑")
        self.assertEqual(content, "出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑")
        self.assertEqual(price, "8000")
        self.assertEqual(status, "待审核")
        self.assertEqual(notice, "请加我的微信")
        self.assertEqual(nickname, "1")
        self.assertEqual(avatar_url, "https://763850.iterator-traits.com/showimage"
                                     "/home/ubuntu/QingXian/media/picture/default_image1.png")
        self.assertEqual(credit, 100)
        self.assertEqual(user_contact, "18800123333")
        self.assertEqual(len(pics), 1)
        pic = pics[0]

        request_dict = {"task_id": task2.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json['price'], "面议")
        self.assertEqual(response_json["status"], "已上架")
        pics = response_json["pics"]
        self.assertEqual(len(pics), 1)
        pic = pics[0]
        self.assertEqual(pic, "https://763850.iterator-traits.com/showimage"
                              "/home/ubuntu/QingXian/media/picture/test.png")

        request_dict = {"task_id": task3.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json['price'], "不高于59元/场")
        self.assertEqual(response_json["status"], "已下架")

        request_dict = {"task_id": task4.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json['price'], "")

    # 测试无效的task_id
    def test_invalid_task_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        request_dict = {"task_id": 100}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试未登录
    def test_no_login_request(self):
        task1 = Task.objects.get(label="出售")

        request_dict = {"task_id": task1.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试查看评论
class GetCommentsTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")

        user = WechatUser.objects.create(open_id="111",
                                         skey="111",
                                         nickname="1",
                                         contact_info="18800123333",
                                         avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image1.png")

        user2 = WechatUser.objects.create(open_id="222",
                                          skey="222",
                                          nickname="2",
                                          contact_info="哈哈哈哈我的手机号码是！！！！！：：：：18800123333",
                                          avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image2.png")

        task1 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="出售",
                                    category="学习",
                                    title="出售笔记本电脑",
                                    detail="出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        Comment.objects.create(reviewer_id=user2.id,
                               receiver_id=user.id,
                               task_id=task1.id,
                               detail="我想买！")

        Comment.objects.create(reviewer_id=user2.id,
                               receiver_id=-1,
                               task_id=task1.id,
                               detail="我想买！")

        self.request_url = "/adminpage/task/get_comments"

    # 测试正常的请求
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        task1 = Task.objects.get(label="出售")

        request_dict = {"task_id": task1.id,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        comment_list = response_json["comment_list"]
        self.assertEqual(len(comment_list), 2)
        comment0 = comment_list[0]
        comment1 = comment_list[1]
        self.assertEqual(comment0["reviewer_nickname"], "2")
        self.assertEqual(comment0["receiver_nickname"], "1")
        self.assertEqual(comment0["detail"], "我想买！")
        self.assertEqual(comment1["receiver_id"], -1)
        self.assertNotIn("receiver_nickname", comment1.keys())

    # 测试无效的task_id
    def test_invalid_task_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        request_dict = {"task_id": 100,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 0)
        comment_list = response_json["comment_list"]
        self.assertEqual(len(comment_list), 0)

    # 测试无效的page
    def test_invalid_page_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        task1 = Task.objects.get(label="出售")

        request_dict = {"task_id": task1.id,
                        "page": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        comment_list = response_json["comment_list"]
        self.assertEqual(len(comment_list), 0)

        request_dict = {"task_id": task1.id,
                        "page": 2}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        comment_list = response_json["comment_list"]
        self.assertEqual(len(comment_list), 0)

    # 测试未登录
    def test_no_login_request(self):
        task1 = Task.objects.get(label="出售")

        request_dict = {"task_id": task1.id,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 任务审批
class TaskCheckTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")

        user = WechatUser.objects.create(open_id="111",
                                         skey="111",
                                         nickname="1",
                                         contact_info="18800123333",
                                         avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image1.png")

        task1 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="出售",
                                    category="学习",
                                    title="出售笔记本电脑",
                                    detail="出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        task2 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="求购",
                                    category="学习",
                                    title="求购笔记本电脑",
                                    detail="求购！！",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        self.request_url = "/adminpage/task/check"

    # 测试不同有效agree的请求
    def test_valid_agree_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        task1 = Task.objects.get(label="出售")
        task2 = Task.objects.get(label="求购")
        user = WechatUser.objects.get(open_id="111")
        # 未审核到上架
        request_dict = {"task_id": task1.id,
                        "agree": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(Notification.objects.all().count(), 1)
        notification = Notification.objects.all()[0]
        self.assertEqual(notification.receiver_id, user.id)
        self.assertEqual(notification.category, 0)
        self.assertEqual(notification.relevant_user_id, -1)
        self.assertEqual(notification.task_id, task1.id)
        self.assertEqual(notification.title, "您发布的任务已经通过审核")
        self.assertEqual(notification.detail, '您发布的"出售笔记本电脑"任务已经通过审核')
        # 未审核到下架
        request_dict = {"task_id": task2.id,
                        "agree": 0,
                        "undercarriage_reason": "不喜欢"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(Notification.objects.all().count(), 2)
        notification = Notification.objects.all()[1]
        self.assertEqual(notification.title, "您发布的任务已经下架")
        self.assertEqual(notification.detail, '您发布的"求购笔记本电脑"任务已经下架。下架原因：不喜欢')
        # 下架到上架
        request_dict = {"task_id": task2.id,
                        "agree": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(Notification.objects.all().count(), 3)
        # 上架到下架
        request_dict = {"task_id": task1.id,
                        "agree": 0,
                        "undercarriage_reason": "不喜欢"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(Notification.objects.all().count(), 4)

    # 测试不同无效agree的请求
    def test_invalid_agree_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        task1 = Task.objects.get(label="出售")
        task2 = Task.objects.get(label="求购")
        # 无效agree
        request_dict = {"task_id": task1.id,
                        "agree": -1,
                        "undercarriage_reason": "不喜欢"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        self.assertEqual(response_json["error"], 1)

        request_dict = {"task_id": task1.id,
                        "agree": 2,
                        "undercarriage_reason": "不喜欢"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        self.assertEqual(response_json["error"], 1)

        # 上架到上架
        task1.status=1
        task1.save()
        request_dict = {"task_id": task1.id,
                        "agree": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        self.assertEqual(response_json["error"], 1)

        # 下架到下架
        task2.status = 2
        task2.save()
        request_dict = {"task_id": task2.id,
                        "agree": 0,
                        "undercarriage_reason": "不喜欢"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        self.assertEqual(response_json["error"], 1)

    # 测试无效task的请求
    def test_invalid_task_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        # 无效task_id
        request_dict = {"task_id": 100,
                        "agree": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        self.assertEqual(response_json["error"], 1)

    # 测试无undercarriage_reason的请求
    def test_no_undercarriage_reason_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        task1 = Task.objects.get(label="出售")
        # 无undercarriage_reason
        request_dict = {"task_id": task1.id,
                        "agree": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        self.assertEqual(response_json["error"], 1)

    # 测试未登录
    def test_no_login_request(self):
        task1 = Task.objects.get(label="出售")

        request_dict = {"task_id": task1.id,
                        "agree": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 修改任务分类
class TaskChangeCategoryTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")

        user = WechatUser.objects.create(open_id="111",
                                         skey="111",
                                         nickname="1",
                                         contact_info="18800123333",
                                         avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image1.png")

        task1 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="出售",
                                    category="学习",
                                    title="出售笔记本电脑",
                                    detail="出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        self.request_url = "/adminpage/task/change_category"

    # 测试不同有效agree的请求
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        task1 = Task.objects.get(label="出售")
        user = WechatUser.objects.get(open_id="111")

        request_dict = {"task_id": task1.id,
                        "category": "其它"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(Notification.objects.all().count(), 1)
        notification = Notification.objects.all()[0]
        self.assertEqual(notification.receiver_id, user.id)
        self.assertEqual(notification.category, 0)
        self.assertEqual(notification.relevant_user_id, -1)
        self.assertEqual(notification.task_id, task1.id)
        self.assertEqual(notification.title, "您发布的任务的类型被修改")
        self.assertEqual(notification.detail, '您发布的"出售笔记本电脑"任务的类型，从"学习"改为"其它"。请注意您发布消息的类型！')

    # 测试无效task的请求
    def test_invalid_task_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        # 无效task_id
        request_dict = {"task_id": 100,
                        "category": "其它"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        self.assertEqual(response_json["error"], 1)

    # 测试无undercarriage_reason的请求
    def test_no_undercarriage_reason_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        task1 = Task.objects.get(label="出售")
        # 无undercarriage_reason
        request_dict = {"task_id": task1.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        self.assertEqual(response_json["error"], 1)

    # 测试未登录
    def test_no_login_request(self):
        task1 = Task.objects.get(label="出售")

        request_dict = {"task_id": task1.id,
                        "category": "其它"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 删除评论
class DeleteCommentTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")

        user = WechatUser.objects.create(open_id="111",
                                         skey="111",
                                         nickname="1",
                                         contact_info="18800123333",
                                         avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image1.png")

        user2 = WechatUser.objects.create(open_id="222",
                                          skey="222",
                                          nickname="2",
                                          contact_info="哈哈哈哈我的手机号码是！！！！！：：：：18800123333",
                                          avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image2.png")

        task1 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="出售",
                                    category="学习",
                                    title="出售笔记本电脑",
                                    detail="出售苹果电脑",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        Comment.objects.create(reviewer_id=user2.id,
                               receiver_id=user.id,
                               task_id=task1.id,
                               detail="我想买！")

        self.request_url = "/adminpage/task/delete_comment"

    # 测试有效的请求
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        task1 = Task.objects.get(label="出售")
        comment = Comment.objects.get(detail="我想买！")
        user2 = WechatUser.objects.get(open_id="222")

        request_dict = {"comment_id": comment.id,
                        "reason": "不合适"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(Notification.objects.all().count(), 1)
        notification = Notification.objects.all()[0]
        self.assertEqual(notification.receiver_id, user2.id)
        self.assertEqual(notification.category, 0)
        self.assertEqual(notification.relevant_user_id, -1)
        self.assertEqual(notification.task_id, task1.id)
        self.assertEqual(notification.title, "您发布的评论被删除")
        self.assertEqual(notification.detail, '您在"出售笔记本电脑"任务下发布的评论"我想买！"被删除。删除原因是"不合适"。请注意您的言辞')

    # 测试无效comment的请求
    def test_invalid_comment_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        # 无效comment_id
        request_dict = {"comment_id": 100,
                        "reason": "不合适"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        self.assertEqual(response_json["error"], 1)

    # 测试无reason的请求
    def test_no_undercarriage_reason_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        # 无reason
        comment = Comment.objects.get(detail="我想买！")
        request_dict = {"comment_id": comment.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        self.assertEqual(response_json["error"], 1)

    # 测试未登录
    def test_no_login_request(self):
        task1 = Task.objects.get(label="出售")

        comment = Comment.objects.get(detail="我想买！")
        request_dict = {"comment_id": comment.id,
                        "reason": "不合适"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 获取用户列表
class GetUserListTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")
        user1 = WechatUser.objects.create(open_id="111",
                                          skey="111",
                                          nickname="1",
                                          contact_info="18800123333",
                                          credit=96,
                                          avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image1.png")
        user2 = WechatUser.objects.create(open_id="222",
                                          skey="222",
                                          nickname="2",
                                          contact_info="18800000000",
                                          credit=100,
                                          avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image2.png")

        task = Task.objects.create(user_id=user1.id,
                                   user_credit=96,
                                   goods_or_activity=0,
                                   label="求购",
                                   category="学习",
                                   title="求购笔记本电脑",
                                   detail="求购苹果电脑",
                                   price_for_goods=-1,
                                   price_for_activity="",
                                   contact_msg="请加我的微信",
                                   status=1)

        Collection.objects.create(user_id=user2.id,
                                  task_id=task.id)
        Comment.objects.create(reviewer_id=user2.id,
                               receiver_id=user2.id,
                               task_id=task.id,
                               detail="我有！")

        self.request_url = "/adminpage/user/get_user_list"

    # 测试有效的请求
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        # 测试全部
        request_dict = {"user_id": -1,
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        user_list = response_json["user_list"]
        self.assertEqual(len(user_list), 2)
        user1 = user_list[0]
        user2 = user_list[1]
        self.assertEqual(user1["nickname"], "1")
        self.assertEqual(user1["user_contact"], "18800123333")
        self.assertEqual(user1["avatar_url"],
                         "https://763850.iterator-traits.com/showimage"
                         "/home/ubuntu/QingXian/media/picture/default_image1.png")
        self.assertEqual(user1["credit"], 96)
        self.assertEqual(user1["task_num"], 1)
        self.assertEqual(user1["comment_num"], 0)
        self.assertEqual(user1["collect_num"], 0)

        self.assertEqual(user2["comment_num"], 1)
        self.assertEqual(user2["collect_num"], 1)

        # 测试有效keyword
        request_dict = {"user_id": -1,
                        "keyword": "1",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        user_list = response_json["user_list"]
        self.assertEqual(len(user_list), 1)
        user1 = user_list[0]
        self.assertEqual(user1["nickname"], "1")

        user = WechatUser.objects.get(nickname="1")
        # 测试有效ID
        request_dict = {"user_id": user.id,
                        "keyword": "哈哈",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        user_list = response_json["user_list"]
        self.assertEqual(len(user_list), 1)
        user1 = user_list[0]
        self.assertEqual(user1["nickname"], "1")

    # 测试无效keyword
    def test_invalid_keyword_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        # 测试全部
        request_dict = {"user_id": -1,
                        "keyword": "3",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 0)
        user_list = response_json["user_list"]
        self.assertEqual(len(user_list), 0)

    # 测试无效ID
    def test_invalid_userid_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        request_dict = {"user_id": 0,
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"user_id": 10,
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无效page
    def test_invalid_page_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        request_dict = {"user_id": -1,
                        "keyword": "",
                        "page": 2}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        user_list = response_json["user_list"]
        self.assertEqual(len(user_list), 0)

        request_dict = {"user_id": -1,
                        "keyword": "",
                        "page": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        user_list = response_json["user_list"]
        self.assertEqual(len(user_list), 0)

    # 测试未登录
    def test_no_login_request(self):
        request_dict = {"user_id": -1,
                        "keyword": "",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 获取用户详情
class GetUserDetailTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")
        user1 = WechatUser.objects.create(open_id="111",
                                          skey="111",
                                          nickname="1",
                                          contact_info="18800123333",
                                          credit=96,
                                          avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image1.png")
        user2 = WechatUser.objects.create(open_id="222",
                                          skey="222",
                                          nickname="2",
                                          contact_info="18800000000",
                                          credit=100,
                                          avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image2.png")

        task = Task.objects.create(user_id=user1.id,
                                   user_credit=96,
                                   goods_or_activity=0,
                                   label="求购",
                                   category="学习",
                                   title="求购笔记本电脑",
                                   detail="求购苹果电脑",
                                   price_for_goods=-1,
                                   price_for_activity="",
                                   contact_msg="请加我的微信",
                                   status=1)

        Collection.objects.create(user_id=user2.id,
                                  task_id=task.id)
        Comment.objects.create(reviewer_id=user2.id,
                               receiver_id=user2.id,
                               task_id=task.id,
                               detail="我有！")

        self.request_url = "/adminpage/user/get_detail"

    # 测试有效的请求
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        user = WechatUser.objects.get(nickname="1")
        request_dict = {"user_id": user.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        user1 = response_json
        self.assertEqual(user1["nickname"], "1")
        self.assertEqual(user1["user_contact"], "18800123333")
        self.assertEqual(user1["avatar_url"],
                         "https://763850.iterator-traits.com/showimage"
                         "/home/ubuntu/QingXian/media/picture/default_image1.png")
        self.assertEqual(user1["credit"], 96)
        self.assertEqual(user1["task_num"], 1)
        self.assertEqual(user1["comment_num"], 0)
        self.assertEqual(user1["collect_num"], 0)

        user = WechatUser.objects.get(nickname="2")
        request_dict = {"user_id": user.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        user2 = response_json
        self.assertEqual(user2["comment_num"], 1)
        self.assertEqual(user2["collect_num"], 1)

    # 测试无效id的请求
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        request_dict = {"user_id": -1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试未登录
    def test_no_login_request(self):
        user = WechatUser.objects.get(nickname="2")
        request_dict = {"user_id": user.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 获取用户所有已发布任务
class GetMyAllTaskTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")

        user = WechatUser.objects.create(open_id="111",
                                         skey="111",
                                         nickname="1",
                                         contact_info="18800123333",
                                         avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")

        user2 = WechatUser.objects.create(open_id="222",
                                          skey="222",
                                          nickname="2",
                                          contact_info="哈哈哈哈我的手机号码是！！！！！：：：：18800123333",
                                          avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")

        task4 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="出售",
                                    category="学习",
                                    title="出售笔记本电脑",
                                    detail="出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        task3 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="求购",
                                    category="学习",
                                    title="求购笔记本电脑",
                                    detail="求购苹果电脑",
                                    price_for_goods=-1,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=1)

        task2 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=1,
                                    label="休闲娱乐",
                                    category="休闲娱乐",
                                    title="一起买笔记本电脑",
                                    detail="找朋友一起笔记本电脑",
                                    price_for_goods=-1,
                                    price_for_activity="不高于59元/场",
                                    contact_msg="请加我的微信",
                                    status=2)

        task1 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=1,
                                    label="失物招领",
                                    category="失物招领",
                                    title="捡到笔记本",
                                    detail="捡到笔记本电脑",
                                    price_for_goods=-1,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        self.request_url = "/adminpage/user/history_task"

    # 测试有效请求
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        user1 = WechatUser.objects.get(nickname="1")
        user2 = WechatUser.objects.get(nickname="2")

        request_dict = {"user_id": user1.id,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 4)
        task0 = data_list[2]
        task1 = data_list[3]
        self.assertEqual(task0["label"], "求购")
        self.assertEqual(task0["category"], "学习")
        self.assertEqual(task0["title"], "求购笔记本电脑")
        self.assertEqual(task0["price"], "面议")
        self.assertEqual(task0["content"], "求购苹果电脑")
        self.assertEqual(task0["status"], "已上架")

        self.assertEqual(task1["price"], "8000")
        self.assertLessEqual(len(task1["content"]), 18)
        if str(task1["content"]).endswith("..."):
            right = 1
        else:
            right = 0
        self.assertEqual(right, 1)
        self.assertEqual(task1["status"], "待审核")

        task0 = data_list[0]
        task1 = data_list[1]
        self.assertLessEqual(task0["price"], "")
        self.assertLessEqual(task1["price"], "不高于59元/场")
        self.assertEqual(task0["status"], "待审核")
        self.assertEqual(task1["status"], "已下架")

        # 没有发过任务的
        request_dict = {"user_id": user2.id,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 0)
        data_list = response_json["data_list"]
        self.assertEqual(len(data_list), 0)

    # 测试无效id的请求
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        request_dict = {"user_id": -1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试未登录
    def test_no_login_request(self):
        user = WechatUser.objects.get(nickname="1")
        request_dict = {"user_id": user.id,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 获取历史评论
class GetHistoryCommentsTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")

        user = WechatUser.objects.create(open_id="111",
                                         skey="111",
                                         nickname="1",
                                         contact_info="18800123333",
                                         avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image1.png")

        user2 = WechatUser.objects.create(open_id="222",
                                          skey="222",
                                          nickname="2",
                                          contact_info="哈哈哈哈我的手机号码是！！！！！：：：：18800123333",
                                          avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image2.png")

        task1 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="出售",
                                    category="学习",
                                    title="出售笔记本电脑",
                                    detail="出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)

        Comment.objects.create(reviewer_id=user2.id,
                               receiver_id=-1,
                               task_id=task1.id,
                               detail="我想买！")

        Comment.objects.create(reviewer_id=user2.id,
                               receiver_id=user.id,
                               task_id=task1.id,
                               detail="我想买！")

        self.request_url = "/adminpage/user/history_comment"

    # 测试正常的请求
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        task = Task.objects.get(label="出售")
        user1 = WechatUser.objects.get(open_id="111")
        user2 = WechatUser.objects.get(open_id="222")
        request_dict = {"user_id": user2.id,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        comment_list = response_json["comment_list"]
        self.assertEqual(len(comment_list), 2)
        comment0 = comment_list[0]
        comment1 = comment_list[1]
        self.assertEqual(comment0["task_id"], task.id)
        self.assertEqual(comment0["receiver_nickname"], "1")
        self.assertEqual(comment0["detail"], "我想买！")

        self.assertEqual(comment1["receiver_id"], -1)
        self.assertNotIn("receiver_nickname", comment1.keys())
        # 未发过评论的用户
        request_dict = {"user_id": user1.id,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 0)
        comment_list = response_json["comment_list"]
        self.assertEqual(len(comment_list), 0)

    # 测试无效的user_id
    def test_invalid_user_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        request_dict = {"task_id": 100,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无效的page
    def test_invalid_page_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        user2 = WechatUser.objects.get(open_id="222")
        request_dict = {"user_id": user2.id,
                        "page": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        comment_list = response_json["comment_list"]
        self.assertEqual(len(comment_list), 0)

        request_dict = {"user_id": user2.id,
                        "page": 2}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["pages"], 1)
        comment_list = response_json["comment_list"]
        self.assertEqual(len(comment_list), 0)

    # 测试未登录
    def test_no_login_request(self):
        user2 = WechatUser.objects.get(open_id="222")
        request_dict = {"user_id": user2.id,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 给用户发消息
class SendMsgTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", email="784824453@qq.com", password="adminpass")

        user = WechatUser.objects.create(open_id="111",
                                         skey="111",
                                         nickname="1",
                                         contact_info="18800123333",
                                         avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image1.png")

        task1 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="出售",
                                    category="学习",
                                    title="出售笔记本电脑",
                                    detail="出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑出售苹果电脑",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=0)
        self.request_url = "/adminpage/user/send_msg"

    # 测试正常参数
    def test_proper_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        task = Task.objects.get(label="出售")
        user1 = WechatUser.objects.get(open_id="111")

        request_dict = {"user_id": user1.id,
                        "detail": "不好",
                        "relevant_task_id": task.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        self.assertEqual(Notification.objects.all().count(), 1)
        notification = Notification.objects.all()[0]
        self.assertEqual(notification.receiver_id, user1.id)
        self.assertEqual(notification.category, 0)
        self.assertEqual(notification.task_id, task.id)
        self.assertEqual(notification.title, "管理员给您发消息")
        self.assertEqual(notification.detail, "不好")
        self.assertEqual(notification.user_check, 0)

        request_dict = {"user_id": user1.id,
                        "detail": "不好",
                        "relevant_task_id": -1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(Notification.objects.all().count(), 2)
        notification = Notification.objects.all()[1]
        self.assertEqual(notification.task_id, -1)

    # 测试无效请求
    def test_invalid_request(self):
        request_dict = {"username": "admin",
                        "password": "adminpass"}
        response_json = json.loads(self.client.post("/adminpage/login", request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)

        # 无效用户
        request_dict = {"user_id": 0,
                        "detail": "不好",
                        "relevant_task_id": -1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        # 测试无效任务
        user = WechatUser.objects.get(open_id="111")
        request_dict = {"user_id": user.id,
                        "detail": "不好",
                        "relevant_task_id": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试未登录
    def test_no_login_request(self):
        user = WechatUser.objects.get(open_id="111")
        request_dict = {"user_id": user.id,
                        "detail": "不好",
                        "relevant_task_id": -1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)
