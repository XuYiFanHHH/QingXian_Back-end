from django.test import TestCase
from wechat.models import *
import json


# 测试用户的头像图片初始化插入
class InsertUserTest(TestCase):
    #  初始化
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            avatar_url="/home/ubuntu/QingXian/media/picture/default_image.png")
        User.objects.create(open_id="123456",
                            skey="123456")
        self.request_url = "/userpage/insert_user"

    # 正确输入测试
    def test_proper_request(self):
        request_dict = {"nickname": "2",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "skey": "123456"}
        response = self.client.post(self.request_url, request_dict)
        error = json.loads(response.content.decode())['error']
        self.assertEqual(error, 0)

    # 错误skey测试
    def test_invalid_skey_request(self):
        request_dict = {"nickname": "2",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "skey": "222"}
        response = self.client.post(self.request_url, request_dict)
        error = json.loads(response.content.decode())['error']
        self.assertEqual(error, 1)

    # 测试无skey输入
    def test_no_skey_request(self):
        request_dict = {"nickname": "2",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png"
                        }
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无nickname输入
    def test_no_nickname_request(self):
        request_dict = {"avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无avatar_url输入
    def test_no_avatar_request(self):
        request_dict = {"nickname": "2",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 重复nickname测试
    def test_repeat_nickname_request(self):
        request_dict = {"nickname": "1",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "skey": "123456"}
        response = self.client.post(self.request_url, request_dict)
        error = json.loads(response.content.decode())['error']
        self.assertEqual(error, 1)


# 测试返回用户信用分,用户信息,头像图片
class GetUserInfoTest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url="/home/ubuntu/QingXian/media/picture/default_image.png")
        User.objects.create(open_id="123456",
                            skey="123456",
                            nickname="2",
                            contact_info="18800122222",
                            credit=96,
                            avatar_url="/home/ubuntu/QingXian/media/picture/default_image.png")
        self.request_url = "/userpage/user/get_user_info"

    #     正确输入测试
    def test_proper_request(self):
        request_dict = {"skey": "123456"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        nickname = response_json["nickname"]
        avatar_url = response_json["avatar_url"]
        credit = response_json["credit"]
        user_contact = response_json["user_contact"]
        self.assertEqual(error, 0)
        self.assertEqual(nickname, "2")
        self.assertEqual(avatar_url, "http://763850.iterator-traits.com/showimage"
                                     "/home/ubuntu/QingXian/media/picture/default_image.png")
        self.assertEqual(credit, 96)
        self.assertEqual(user_contact, "18800122222")

    # 测试不存在的skey输入
    def test_invalid_skey_request(self):
        request_dict = {"skey": "123456"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无skey输入
    def test_invalid_skey_request(self):
        request_dict = {}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试更改用户信息
class UpdateUserInfoTest(TestCase):
    #  初始化
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            avatar_url="")
        User.objects.create(open_id="1234567",
                            skey="1234567",
                            nickname="3",
                            avatar_url="")
        self.request_url = "/userpage/user/update_user_info"

    # 正确输入测试
    def test_proper_request(self):
        request_dict = {"nickname": "2",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "skey": "654321",
                        "user_contact": "23558121"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        user = User.objects.get(skey="654321")
        self.assertEqual(user.nickname, "2")
        self.assertEqual(user.avatar_url, "/home/ubuntu/QingXian/media/picture/default_image.png")
        self.assertEqual(user.contact_info, "23558121")
        self.assertEqual(error, 0)

    # 错误skey测试
    def test_invalid_skey_request(self):
        request_dict = {"nickname": "2",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "user_contact": "23558121",
                        "skey": "222"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无skey输入
    def test_no_skey_request(self):
        request_dict = {"nickname": "2",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "user_contact": "23558121"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无nickname输入
    def test_no_nickname_request(self):
        request_dict = {"avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "user_contact": "23558121",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无avatar_url输入
    def test_no_avatar_request(self):
        request_dict = {"nickname": "2",
                        "user_contact": "23558121",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无user_contact输入
    def test_no_user_contact_request(self):
        request_dict = {"avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "nickname": "2",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 重复nickname测试
    def test_repeat_nickname_request(self):
        request_dict = {"nickname": "3",
                        "user_contact": "23558121",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试用户反馈
class UserFeedbackRequest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            avatar_url="")
        self.request_url = "/userpage/user/feedback"

    # 正确输入测试
    def test_proper_request(self):
        pre_length = Feedback.objects.all().count()
        request_dict = {"detail": "nothing",
                        "pics": "",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        afterward_length = Feedback.objects.all().count()
        self.assertEqual(afterward_length, pre_length+1)
        feedback = Feedback.objects.all().order_by("-release_time")[0]
        user = User.objects.get(skey="654321")
        self.assertEqual(feedback.user_id, user.id)
        self.assertEqual(feedback.detail, "nothing")

    # 错误skey测试
    def test_invalid_skey_request(self):
        request_dict = {"detail": "nothing",
                        "pics": "",
                        "skey": "222"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无skey输入
    def test_no_skey_request(self):
        request_dict = {"detail": "nothing",
                        "pics": ""}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无pics输入
    def test_no_pics_request(self):
        request_dict = {"detail": "nothing",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无detail输入
    def test_no_detail_request(self):
        request_dict = {"skey": "654321",
                        "pics": ""}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试发布任务
class CreateTaskRequest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            avatar_url="")
        self.request_url = "/userpage/create_task"

    # 正确输入,无图片测试
    def test_no_pic_request(self):
        request_dict = {"goods_or_activity": 0,
                        "label": "求购",
                        "category": "学习",
                        "title": "求购笔记本电脑",
                        "detail": "求购苹果电脑",
                        "price": 8000,
                        "pics": None,
                        "notice": "请加我的微信",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        length = Task.objects.all().count()
        self.assertEqual(length, 1)
        user = User.objects.get(skey="654321")
        task = Task.objects.get(user_id=user.id)
        self.assertEqual(task.user_credit, user.credit)
        self.assertEqual(task.goods_or_activity, 0)
        self.assertEqual(task.label, "求购")
        self.assertEqual(task.title, "求购笔记本电脑")
        self.assertEqual(task.detail, "求购苹果电脑")
        self.assertEqual(task.category, "学习")
        self.assertEqual(task.price_for_goods, 8000)
        self.assertEqual(task.contact_msg, "请加我的微信")
        self.assertEqual(task.status, 0)

    # 正确输入,有图片测试
    def test_with_pic_request(self):
        request_dict = {"goods_or_activity": 0,
                        "label": "求购",
                        "category": "学习",
                        "title": "求购笔记本电脑",
                        "detail": "求购苹果电脑",
                        "price": 8000,
                        "pics": ["/home/ubuntu/QingXian/media/picture/default_image.png"],
                        "notice": "请加我的微信",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        length = Task.objects.all().count()
        self.assertEqual(length, 1)
        user = User.objects.get(skey="654321")
        task = Task.objects.get(user_id=user.id)
        self.assertEqual(task.user_credit, user.credit)
        self.assertEqual(task.goods_or_activity, 0)
        self.assertEqual(task.label, "求购")
        self.assertEqual(task.title, "求购笔记本电脑")
        self.assertEqual(task.detail, "求购苹果电脑")
        self.assertEqual(task.category, "学习")
        self.assertEqual(task.price_for_goods, 8000)
        self.assertEqual(task.contact_msg, "请加我的微信")
        self.assertEqual(task.status, 0)
        length = Picture.objects.all().count()
        self.assertEqual(length, 1)
        picture = Picture.objects.get(task_id=task.id)
        self.assertEqual(picture.picture_url, "/home/ubuntu/QingXian/media/picture/default_image.png")

    # 错误skey测试
    def test_invalid_skey_request(self):
        request_dict = {"goods_or_activity": 0,
                        "label": "求购",
                        "category": "学习",
                        "title": "求购笔记本电脑",
                        "detail": "求购苹果电脑",
                        "price": 8000,
                        "pics": [],
                        "notice": "请加我的微信",
                        "skey": "222"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无skey输入
    def test_no_skey_request(self):
        request_dict = {"goods_or_activity": 0,
                        "label": "求购",
                        "category": "学习",
                        "title": "求购笔记本电脑",
                        "detail": "求购苹果电脑",
                        "price": 8000,
                        "pics": [],
                        "notice": "请加我的微信"}
        response_json = json.loads(self.client.post(self.request_url, request_dict).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

