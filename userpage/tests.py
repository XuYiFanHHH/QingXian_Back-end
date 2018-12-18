from django.test import TestCase
from QingXian.settings import *
from wechat.models import *
import json
import time


# 测试查看skey
class CheckSkeyTest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        self.request_url = "/userpage/check_skey"

    # 正确输入测试
    def test_proper_request(self):
        request_dict = {"skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        valid = response_json['valid']
        self.assertEqual(valid, 1)

    # 测试不存在的skey输入
    def test_invalid_skey_request(self):
        request_dict = {"skey": "123456"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        valid = response_json['valid']
        self.assertEqual(valid, 0)

    # 测试无skey输入
    def test_no_skey_request(self):
        request_dict = {}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试用户的头像图片初始化插入
class InsertUserTest(TestCase):
    #  初始化
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        User.objects.create(open_id="123456",
                            skey="123456")
        self.request_url = "/userpage/insert_user"

    # 正确输入测试
    def test_proper_request(self):
        request_dict = {"nickname": "2",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "skey": "123456"}
        response = self.client.post(self.request_url, request_dict, secure=True)
        error = json.loads(response.content.decode())['error']
        self.assertEqual(error, 0)

    # 错误skey测试
    def test_invalid_skey_request(self):
        request_dict = {"nickname": "2",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "skey": "222"}
        response = self.client.post(self.request_url, request_dict, secure=True)
        error = json.loads(response.content.decode())['error']
        self.assertEqual(error, 1)

    # 测试无skey输入
    def test_no_skey_request(self):
        request_dict = {"nickname": "2",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png"
                        }
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无nickname输入
    def test_no_nickname_request(self):
        request_dict = {"avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无avatar_url输入
    def test_no_avatar_request(self):
        request_dict = {"nickname": "2",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试返回用户信用分,用户信息,头像图片
class GetUserInfoTest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        User.objects.create(open_id="123456",
                            skey="123456",
                            nickname="2",
                            contact_info="18800122222",
                            credit=96,
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        self.request_url = "/userpage/user/get_user_info"

    # 正确输入测试
    def test_proper_request(self):
        request_dict = {"skey": "123456"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        nickname = response_json["nickname"]
        avatar_url = response_json["avatar_url"]
        credit = response_json["credit"]
        user_contact = response_json["user_contact"]
        self.assertEqual(error, 0)
        self.assertEqual(nickname, "2")
        self.assertEqual(avatar_url, "https://763850.iterator-traits.com/showimage"
                                     "/home/ubuntu/QingXian/media/picture/default_image.png")
        self.assertEqual(credit, 96)
        self.assertEqual(user_contact, "18800122222")

    # 测试不存在的skey输入
    def test_invalid_skey_request(self):
        request_dict = {"skey": "2222"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无skey输入
    def test_no_skey_request(self):
        request_dict = {}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
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
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
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
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无skey输入
    def test_no_skey_request(self):
        request_dict = {"nickname": "2",
                        "avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "user_contact": "23558121"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无nickname输入
    def test_no_nickname_request(self):
        request_dict = {"avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "user_contact": "23558121",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无avatar_url输入
    def test_no_avatar_request(self):
        request_dict = {"nickname": "2",
                        "user_contact": "23558121",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无user_contact输入
    def test_no_user_contact_request(self):
        request_dict = {"avatar_url": "/home/ubuntu/QingXian/media/picture/default_image.png",
                        "nickname": "2",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
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
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
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
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无skey输入
    def test_no_skey_request(self):
        request_dict = {"detail": "nothing",
                        "pics": ""}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无pics输入
    def test_no_pics_request(self):
        request_dict = {"detail": "nothing",
                        "skey": "654321"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无detail输入
    def test_no_detail_request(self):
        request_dict = {"skey": "654321",
                        "pics": ""}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
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
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
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
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
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
                        "pics": None,
                        "notice": "请加我的微信",
                        "skey": "222"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
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
                        "pics": None,
                        "notice": "请加我的微信"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试获取上架任务总数
class GetValidTaskNumberTest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        user = User.objects.get(open_id="654321")
        Task.objects.create(user_id=user.id,
                            user_credit=100,
                            goods_or_activity=0,
                            label="求购",
                            category="学习",
                            title="求购笔记本电脑",
                            detail="求购苹果电脑",
                            price_for_goods=8000,
                            price_for_activity="",
                            contact_msg="请加我的微信",
                            status=1)
        Task.objects.create(user_id=user.id,
                            user_credit=100,
                            goods_or_activity=0,
                            label="求购",
                            category="学习",
                            title="求购笔记本电脑",
                            detail="求购苹果电脑",
                            price_for_goods=8000,
                            price_for_activity="",
                            contact_msg="请加我的微信",
                            status=0)
        Task.objects.create(user_id=user.id,
                            user_credit=100,
                            goods_or_activity=1,
                            label="休闲娱乐",
                            category="休闲娱乐",
                            title="一起看电影",
                            detail="找朋友一起看电影",
                            price_for_goods=-1,
                            price_for_activity="",
                            contact_msg="请加我的微信",
                            status=1)
        Task.objects.create(user_id=user.id,
                            user_credit=100,
                            goods_or_activity=1,
                            label="休闲娱乐",
                            category="休闲娱乐",
                            title="一起看电影",
                            price_for_goods=-1,
                            price_for_activity="",
                            detail="找朋友一起看电影",
                            contact_msg="请加我的微信",
                            status=0)
        self.request_url = "/userpage/task/get_number"

    # 正确输入测试
    def test_proper_request(self):
        request_dict = {"skey": "654321",
                        "goods_or_activity": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        valid = response_json['number']
        self.assertEqual(valid, 1)

        request_dict = {"skey": "654321",
                        "goods_or_activity": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        valid = response_json['number']
        self.assertEqual(valid, 1)

    # 测试不存在的skey输入
    def test_invalid_skey_request(self):
        request_dict = {"skey": "123456",
                        "goods_or_activity": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"skey": "123456",
                        "goods_or_activity": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无skey输入
    def test_no_skey_request(self):
        request_dict = {"goods_or_activity": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)
        request_dict = {"goods_or_activity": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 错误goods_or_activity测试
    def test_invalid_request(self):
        request_dict = {"skey": "654321",
                        "goods_or_activity": -1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"skey": "654321",
                        "goods_or_activity": 2}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试获取上架任务
class GetTaskTest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        User.objects.create(open_id="222",
                            skey="222",
                            nickname="2",
                            contact_info="18800000000",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        user = User.objects.get(open_id="654321")
        task = Task.objects.create(user_id=user.id,
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
                               task_id=task.id,
                               feedback_id=-1)

        test_user = User.objects.get(open_id="222")
        Collection.objects.create(user_id=test_user.id,
                                  task_id=task.id)
        Comment.objects.create(reviewer_id=test_user.id,
                               receiver_id=user.id,
                               task_id=task.id,
                               detail="我有！")

        Task.objects.create(user_id=user.id,
                            user_credit=96,
                            goods_or_activity=0,
                            label="出售",
                            category="学习",
                            title="出售笔记本电脑",
                            detail="出售苹果电脑",
                            price_for_goods=8000,
                            price_for_activity="",
                            contact_msg="请加我的微信",
                            status=1)

        Task.objects.create(user_id=user.id,
                            user_credit=100,
                            goods_or_activity=0,
                            label="求购",
                            category="学习",
                            title="求购笔记本电脑",
                            detail="求购苹果电脑",
                            price_for_goods=8000,
                            price_for_activity="",
                            contact_msg="请加我的微信",
                            status=0)

        Task.objects.create(user_id=user.id,
                            user_credit=100,
                            goods_or_activity=1,
                            label="休闲娱乐",
                            category="休闲娱乐",
                            title="一起看电影",
                            detail="找朋友一起看电影",
                            price_for_goods=-1,
                            price_for_activity="不高于59元/场",
                            contact_msg="请加我的微信",
                            status=1)

        Task.objects.create(user_id=user.id,
                            user_credit=96,
                            goods_or_activity=1,
                            label="失物招领",
                            category="失物招领",
                            title="捡到笔记本",
                            detail="捡到笔记本电脑",
                            price_for_goods=-1,
                            price_for_activity="",
                            contact_msg="请加我的微信",
                            status=1)

        Task.objects.create(user_id=user.id,
                            user_credit=100,
                            goods_or_activity=1,
                            label="休闲娱乐",
                            category="休闲娱乐",
                            title="一起看电影",
                            price_for_goods=-1,
                            price_for_activity="",
                            detail="找朋友一起看电影",
                            contact_msg="请加我的微信",
                            status=0)
        self.request_url = "/userpage/task/get_all"

    # 正确输入测试,goods_or_activity（按时间倒排）
    def test_proper_goods_or_activity_request(self):
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 2)
        task1 = data_list[0]
        task2 = data_list[1]
        user = User.objects.get(open_id="654321")
        self.assertEqual(task1["label"], "出售")
        self.assertEqual(task1["title"], "出售笔记本电脑")
        self.assertEqual(task1["detail"], "出售苹果电脑")
        self.assertEqual(task1["price"], "8000")
        self.assertEqual(task1["user_id"], user.id)
        self.assertEqual(task1["user_nickname"], user.nickname)
        self.assertEqual(task1["user_avatar"],user.avatar_url)
        self.assertEqual(len(task1["pics"]), 0)
        self.assertEqual(task1["collect_num"], 0)
        self.assertEqual(task1["hasCollect"], 0)

        self.assertEqual(task2["pic"],
                         "https://763850.iterator-traits.com/showimage" +
                         "/home/ubuntu/QingXian/media/picture/test.png")
        self.assertEqual(len(task2["pics"]), 1)
        self.assertEqual(task2["pics"][0],
                         "https://763850.iterator-traits.com/showimage" +
                         "/home/ubuntu/QingXian/media/picture/test.png")
        self.assertEqual(task2["collect_num"], 1)
        self.assertEqual(task2["hasCollect"], 1)
        self.assertEqual(task2["price"], "面议")
        self.assertGreaterEqual(int(task1["submit_time_count"]), int(task2["submit_time_count"]))

        # 除了价格的表述，其余的各个键值对取法相同
        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 2)
        task1 = data_list[0]
        task2 = data_list[1]
        self.assertEqual(task2["price"], "不高于59元/场")
        self.assertEqual(task1["price"], "无价位要求")

    # category测试
    def test_category_request(self):
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "学习",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 2)

        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "休闲娱乐",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 1)

        # 不存在的category
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "休闲娱乐",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 0)

        # 不存在的category
        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "休闲",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 0)

    # keyword测试
    def test_keyword_request(self):
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "全部",
                        "keyword": "电脑",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 2)

        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "全部",
                        "keyword": "电脑",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 1)

        # 关键词不为空，则应该不用考虑category
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "生活",
                        "keyword": "电脑",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 2)

        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "生活",
                        "keyword": "电脑",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 1)

        # 关键词不存在
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "生活",
                        "keyword": "哈哈",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 0)

        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "生活",
                        "keyword": "哈哈",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 0)

    # select_index测试（0取值之前测过）
    def test_select_index_request(self):
        # 商品select_index=1，只看出售
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 1,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0]["label"], "出售")
        # 商品select_index=2，只看求购
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 2,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0]["label"], "求购")

        # 消息活动select_index=1，只看有价格
        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 1,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0]["price"], "不高于59元/场")
        # 消息活动select_index=2，只看无价格
        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 2,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0]["price"], "无价位要求")

        # 错误的select_index
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "全部",
                        "keyword": "",
                        "select_index": -1,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # sort_index测试（0取值之前测过）
    def test_sort_index_request(self):
        # 商品sort_index=1，发布时间升序
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 2)
        self.assertEqual(data_list[0]["label"], "求购")
        self.assertEqual(data_list[1]["label"], "出售")
        # 消息活动sort_index=1，发布时间升序
        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 2)
        self.assertEqual(data_list[0]["label"], "休闲娱乐")
        self.assertEqual(data_list[1]["label"], "失物招领")

        # 商品sort_index=2，价格降序
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 2,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 2)
        self.assertEqual(data_list[0]["label"], "出售")
        self.assertEqual(data_list[1]["label"], "求购")
        # 消息活动sort_index=2，信用降序
        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 2,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 2)
        self.assertEqual(data_list[0]["label"], "休闲娱乐")
        self.assertEqual(data_list[1]["label"], "失物招领")

        # 商品sort_index=3，价格升序
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 3,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 2)
        self.assertEqual(data_list[0]["label"], "求购")
        self.assertEqual(data_list[1]["label"], "出售")
        # 消息活动sort_index=3，报错
        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 3,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        # 商品sort_index=4，信用降序
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 4,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['data_list']
        self.assertEqual(len(data_list), 2)
        self.assertEqual(data_list[0]["label"], "求购")
        self.assertEqual(data_list[1]["label"], "出售")
        # 消息活动sort_index=4，报错
        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 4,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试不存在的skey输入
    def test_invalid_skey_request(self):
        request_dict = {"skey": "2333",
                        "goods_or_activity": 1,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无skey输入
    def test_no_skey_request(self):
        request_dict = {"goods_or_activity": 1,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 错误goods_or_activity测试
    def test_invalid_goods_or_activity_request(self):
        request_dict = {"skey": "222",
                        "goods_or_activity": -1,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"skey": "222",
                        "goods_or_activity": 2,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 无效page测试
    def test_invalid_page_request(self):
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(len(response_json['data_list']), 0)

        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "category": "全部",
                        "keyword": "",
                        "select_index": 0,
                        "sort_index": 0,
                        "page": 2}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(len(response_json['data_list']), 0)


# 测试获取任务详情
class GetTaskDetailTest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        User.objects.create(open_id="222",
                            skey="222",
                            nickname="2",
                            contact_info="18800000000",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        user = User.objects.get(open_id="654321")
        task = Task.objects.create(user_id=user.id,
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
                               task_id=task.id,
                               feedback_id=-1)

        test_user = User.objects.get(open_id="222")
        Collection.objects.create(user_id=test_user.id,
                                  task_id=task.id)
        Comment.objects.create(reviewer_id=test_user.id,
                               receiver_id=user.id,
                               task_id=task.id,
                               detail="我有！")

        Task.objects.create(user_id=user.id,
                            user_credit=100,
                            goods_or_activity=0,
                            label="出售",
                            category="学习",
                            title="出售笔记本电脑",
                            detail="出售苹果电脑",
                            price_for_goods=8000,
                            price_for_activity="",
                            contact_msg="请加我的微信",
                            status=1)

        Task.objects.create(user_id=user.id,
                            user_credit=100,
                            goods_or_activity=1,
                            label="休闲娱乐",
                            category="休闲娱乐",
                            title="一起看电影",
                            detail="找朋友一起看电影",
                            price_for_goods=-1,
                            price_for_activity="不高于59元/场",
                            contact_msg="请加我的微信",
                            status=1)

        Task.objects.create(user_id=user.id,
                            user_credit=100,
                            goods_or_activity=1,
                            label="失物招领",
                            category="失物招领",
                            title="捡到笔记本",
                            detail="捡到笔记本电脑",
                            price_for_goods=-1,
                            price_for_activity="",
                            contact_msg="请加我的微信",
                            status=1)
        self.request_url = "/userpage/task/detail"

    # 测试正常输入
    def test_proper_request(self):
        task1 = Task.objects.get(label="求购")
        task2 = Task.objects.get(label="出售")
        task3 = Task.objects.get(label="休闲娱乐")
        task4 = Task.objects.get(label="失物招领")

        # 商品 有评论 有图片 收藏
        request_dict = {"skey": "222",
                        "task_id": task1.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["title"], "求购笔记本电脑")
        self.assertEqual(response_json["detail"], "求购苹果电脑")
        self.assertEqual(response_json["price"], "面议")
        self.assertEqual(response_json["user_credit"], 100)
        self.assertEqual(response_json["nickname"], "1")
        self.assertEqual(response_json["avatar"],
                         "https://763850.iterator-traits.com/showimage"+
                         "/home/ubuntu/QingXian/media/picture/default_image.png")
        self.assertEqual(len(response_json["pics"]), 1)
        self.assertEqual(response_json["pics"][0],
                         "https://763850.iterator-traits.com/showimage" +
                         "/home/ubuntu/QingXian/media/picture/test.png")
        self.assertEqual(len(response_json["comment_list"]), 1)
        comment = response_json["comment_list"][0]
        self.assertEqual(comment["reviewer_nickname"], "2")
        self.assertEqual(comment["receiver_nickname"], "1")
        self.assertEqual(comment["detail"], "我有！")
        self.assertEqual(response_json["hasCollect"], 1)

        # 商品 无上传图片，无评论 未收藏
        request_dict = {"skey": "222",
                        "task_id": task2.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["price"], "8000")
        self.assertEqual(len(response_json["pics"]), 1)
        self.assertEqual(response_json["hasCollect"], 0)

        # 消息活动 有价格
        request_dict = {"skey": "222",
                        "task_id": task3.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["price"], "不高于59元/场")

        # 消息活动 无价格
        request_dict = {"skey": "222",
                        "task_id": task4.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["price"], "无价位要求")

    # 测试不存在的task_id
    def test_invalid_taskid_request(self):
        request_dict = {"skey": "222",
                        "task_id": 100}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)



    # 测试无效的skey输入
    def test_invalid_skey_request(self):
        task1 = Task.objects.get(label="求购")
        request_dict = {"skey": "2333",
                        "task_id": task1.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"task_id": task1.id}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试get_publisher_contact
class GetPublisherContactTest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        User.objects.create(open_id="222",
                            skey="222",
                            nickname="2",
                            contact_info="18800000000",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        User.objects.create(open_id="333",
                            skey="333",
                            nickname="3",
                            contact_info="",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        user = User.objects.get(open_id="654321")
        Task.objects.create(user_id=user.id,
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
        self.request_url = "/userpage/task/get_publisher_contact"

    # 测试正常输入
    def test_proper_request(self):
        task = Task.objects.get(label="求购")
        # 已经填写联系方式, 用户未看到
        request_dict = {"skey": "222",
                        "task_id": task.id,
                        "complete": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["user_contact"], "18800123333")
        self.assertEqual(response_json["notice"], "请加我的微信")
        self.assertEqual(response_json["self_contact_complete"], 1)
        self.assertEqual(Notification.objects.all().count(), 0)

        # 是自己发布的任务,不发通知
        request_dict = {"skey": "654321",
                        "task_id": task.id,
                        "complete": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(Notification.objects.all().count(), 0)

        # 已经填写联系方式, 用户看到，发送通知
        request_dict = {"skey": "222",
                        "task_id": task.id,
                        "complete": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(Notification.objects.all().count(), 1)
        notification = Notification.objects.all()[0]
        self.assertEqual(notification.task_id, task.id)
        self.assertEqual(notification.category, 1)
        self.assertEqual(notification.title, "2 获取了你的联系方式")
        self.assertEqual(notification.user_check, 0)

        # 未填写联系方式
        request_dict = {"skey": "333",
                        "task_id": task.id,
                        "complete": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["self_contact_complete"], 0)

    # 测试不存在的task_id
    def test_invalid_taskid_request(self):
        request_dict = {"skey": "222",
                        "task_id": 100,
                        "complete": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无效的skey输入
    def test_invalid_skey_request(self):
        task1 = Task.objects.get(label="求购")
        request_dict = {"skey": "2333",
                        "task_id": task1.id,
                        "complete": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"task_id": task1.id,
                        "complete": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试comment
class CommentTest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        User.objects.create(open_id="222",
                            skey="222",
                            nickname="2",
                            contact_info="18800000000",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        user = User.objects.get(open_id="654321")
        Task.objects.create(user_id=user.id,
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
        self.request_url = "/userpage/task/comment"

    # 测试正常输入
    def test_proper_request(self):
        task = Task.objects.get(label="求购")
        user = User.objects.get(open_id="654321")
        # 对任务的评论
        request_dict = {"skey": "222",
                        "task_id": task.id,
                        "receiver_id": -1,
                        "detail": "我有一台！"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(Comment.objects.all().count(), 1)
        comment = Comment.objects.all()[0]
        self.assertEqual(comment.detail, "我有一台！")
        self.assertEqual(comment.task_id, task.id)
        notification = Notification.objects.all()[0]
        self.assertEqual(notification.task_id, task.id)
        self.assertEqual(notification.category, 1)
        self.assertEqual(notification.title, "2 评论了你的发布任务")
        self.assertEqual(notification.detail, "我有一台！")
        self.assertEqual(notification.user_check, 0)

        request_dict = {"skey": "222",
                        "task_id": task.id,
                        "receiver_id": user.id,
                        "detail": "我有一台！"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(Comment.objects.all().count(), 2)
        comment = Comment.objects.all()[1]
        self.assertEqual(comment.detail, "我有一台！")
        self.assertEqual(comment.task_id, task.id)
        notification = Notification.objects.all()[1]
        self.assertEqual(notification.task_id, task.id)
        self.assertEqual(notification.category, 1)
        self.assertEqual(notification.title, "2 回复了你的评论")
        self.assertEqual(notification.detail, "我有一台！")
        self.assertEqual(notification.user_check, 0)

    # 测试不存在的task_id
    def test_invalid_taskid_request(self):
        request_dict = {"skey": "222",
                        "task_id": 100,
                        "receiver_id": -1,
                        "detail": "我有一台！"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 测试无效的skey输入
    def test_invalid_skey_request(self):
        task1 = Task.objects.get(label="求购")
        request_dict = {"skey": "2333",
                        "task_id": task1.id,
                        "receiver_id": -1,
                        "detail": "我有一台！"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"task_id": task1.id,
                        "receiver_id": -1,
                        "detail": "我有一台！"}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试关注/取关任务
class CollectTest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        User.objects.create(open_id="222",
                            skey="222",
                            nickname="2",
                            contact_info="18800000000",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        user = User.objects.get(open_id="654321")
        task = Task.objects.create(user_id=user.id,
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
        test_user = User.objects.get(open_id="222")
        Collection.objects.create(user_id=test_user.id,
                                  task_id=task.id)
        self.request_url = "/userpage/task/collect"

    # 测试正常输入
    def test_proper_request(self):
        task = Task.objects.get(label="求购")
        user = User.objects.get(open_id="654321")
        # 取消关注
        request_dict = {"skey": "222",
                        "task_id": task.id,
                        "collect_id": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["hasCollect"], 0)
        # 关注
        request_dict = {"skey": "222",
                        "task_id": task.id,
                        "collect_id": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["hasCollect"], 1)

    # 测试无效的skey输入
    def test_invalid_skey_request(self):
        task1 = Task.objects.get(label="求购")
        request_dict = {"skey": "2333",
                        "task_id": task1.id,
                        "collect_id": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"task_id": task1.id,
                        "collect_id": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)


# 测试get_notifications
class GetNotificationsTest(TestCase):
    def setUp(self):
        User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        User.objects.create(open_id="222",
                            skey="222",
                            nickname="2",
                            contact_info="18800000000",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/test.png")
        user = User.objects.get(open_id="654321")

        task = Task.objects.create(user_id=user.id,
                                   user_credit=100,
                                   goods_or_activity=0,
                                   label="求购",
                                   category="学习",
                                   title="求购笔记本电脑",
                                   detail="求购苹果电脑!求购苹果电脑!求购苹果电脑!求购苹果电脑!"
                                          "求购苹果电脑!求购苹果电脑!求购苹果电脑!求购苹果电脑!求购苹果电脑!",
                                   price_for_goods=-1,
                                   price_for_activity="",
                                   contact_msg="请加我的微信",
                                   status=1)

        title = "您发布的任务已经通过审核"
        detail = '您发布的任务已经通过审核'
        notification = Notification(receiver_id=task.user_id,
                                    category=0,
                                    comment_id=-1,
                                    relevant_user_id=-1,
                                    task_id=task.id,
                                    title=title,
                                    detail=detail,
                                    user_check=0)
        notification.save()
        test_user = User.objects.get(open_id="222")
        title = test_user.nickname + " 获取了你的联系方式"
        notification = Notification(receiver_id=task.user_id,
                                    category=1,
                                    comment_id=-1,
                                    relevant_user_id=test_user.id,
                                    task_id=task.id,
                                    title=title,
                                    detail="哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈"
                                           "哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈",
                                    user_check=0)
        notification.save()
        self.request_url = "/userpage/message"

    # 测试正常输入
    def test_proper_request(self):
        task = Task.objects.get(label="求购")
        request_dict = {"skey": "654321",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(response_json["system_notice_count"], 1)
        user_notices = response_json['user_notice_list']
        self.assertEqual(len(user_notices), 1)
        notice = user_notices[0]
        self.assertEqual(notice["task_id"], task.id)
        self.assertEqual(notice["title"], "2 获取了你的联系方式")
        self.assertEqual(notice["task_title"], "求购笔记本电脑")
        self.assertLessEqual(len(notice["content"]), 28)
        if str(notice["content"]).endswith("..."):
            right = 1
        else:
            right = 0
        self.assertEqual(right, 1)
        avatar_url = "https://763850.iterator-traits.com/showimage/home/ubuntu/QingXian/media/picture/test.png"
        self.assertEqual(notice["user_avatar_url"],avatar_url)
        self.assertEqual(notice["task_image_url"], "")

        Picture.objects.create(picture_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/test.png",
                               task_id=task.id,
                               feedback_id=-1)
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        user_notices = response_json['user_notice_list']
        notice = user_notices[0]
        image_url = "https://763850.iterator-traits.com/showimage/home/ubuntu/QingXian/media/picture/test.png"
        self.assertEqual(notice["task_image_url"], image_url)

    # 测试无效的skey输入
    def test_invalid_skey_request(self):
        task1 = Task.objects.get(label="求购")
        request_dict = {"skey": "2333",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 无效page测试
    def test_invalid_page_request(self):
        request_dict = {"skey": "654321",
                        "page": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(len(response_json['user_notice_list']), 0)

        request_dict = {"skey": "654321",
                        "page": 2}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(len(response_json['user_notice_list']), 0)


# 测试get_system_notifications
class GetSystemNotificationsTest(TestCase):
    def setUp(self):
        user = User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")

        task = Task.objects.create(user_id=user.id,
                                   user_credit=100,
                                   goods_or_activity=0,
                                   label="求购",
                                   category="学习",
                                   title="求购笔记本电脑",
                                   detail="求购苹果电脑!求购苹果电脑!求购苹果电脑!求购苹果电脑!"
                                          "求购苹果电脑!求购苹果电脑!求购苹果电脑!求购苹果电脑!求购苹果电脑!",
                                   price_for_goods=-1,
                                   price_for_activity="",
                                   contact_msg="请加我的微信",
                                   status=1)

        title = "您发布的任务已经通过审核"
        detail = '您发布的"' + task.title + '"任务已经通过审核'
        notification = Notification(receiver_id=task.user_id,
                                    category=0,
                                    comment_id=-1,
                                    relevant_user_id=-1,
                                    task_id=task.id,
                                    title=title,
                                    detail=detail,
                                    user_check=0)
        notification.save()
        self.request_url = "/userpage/message/system_notification"

    # 测试正常输入
    def test_proper_request(self):
        task = Task.objects.get(label="求购")
        request_dict = {"skey": "654321",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        notices = response_json['notice_list']
        self.assertEqual(len(notices), 1)
        notice = notices[0]
        self.assertEqual(notice["task_id"], task.id)
        self.assertEqual(notice["title"], "您发布的任务已经通过审核")
        self.assertEqual(notice["content"], '您发布的"' + '求购笔记本电脑' + '"任务已经通过审核')

    # 测试无效的skey输入
    def test_invalid_skey_request(self):
        task1 = Task.objects.get(label="求购")
        request_dict = {"skey": "2333",
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 无效page测试
    def test_invalid_page_request(self):
        request_dict = {"skey": "654321",
                        "page": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(len(response_json['notice_list']), 0)

        request_dict = {"skey": "654321",
                        "page": 2}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(len(response_json['notice_list']), 0)


# 测试我的关注
class GetMyCollectionTest(TestCase):
    def setUp(self):
        user = User.objects.create(open_id="654321",
                            skey="654321",
                            nickname="1",
                            contact_info="18800123333",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")

        test_user = User.objects.create(open_id="222",
                            skey="222",
                            nickname="2",
                            contact_info="18800000000",
                            avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")

        task1 = Task.objects.create(user_id=user.id,
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
                               task_id=task1.id,
                               feedback_id=-1)

        task2 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="出售",
                                    category="学习",
                                    title="出售笔记本电脑",
                                    detail="出售苹果电脑",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=2)

        task3 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=1,
                                    label="休闲娱乐",
                                    category="休闲娱乐",
                                    title="一起看电影",
                                    detail="找朋友一起看电影",
                                    price_for_goods=-1,
                                    price_for_activity="不高于59元/场",
                                    contact_msg="请加我的微信",
                                    status=1)

        task4 = Task.objects.create(user_id=user.id,
                                    user_credit=96,
                                    goods_or_activity=1,
                                    label="失物招领",
                                    category="失物招领",
                                    title="捡到笔记本",
                                    detail="捡到笔记本电脑",
                                    price_for_goods=-1,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=1)

        Collection.objects.create(user_id=test_user.id,
                                  task_id=task4.id)

        Collection.objects.create(user_id=test_user.id,
                                  task_id=task3.id)

        Collection.objects.create(user_id=test_user.id,
                                  task_id=task2.id)

        Collection.objects.create(user_id=test_user.id,
                                  task_id=task1.id)

        self.request_url = "/userpage/user/my_collection"

    # 正确输入测试
    def test_proper_request(self):
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['task_list']
        self.assertEqual(len(data_list), 2)
        task1 = data_list[0]
        task2 = data_list[1]
        self.assertEqual(task2["label"], "出售")
        self.assertEqual(task2["title"], "出售笔记本电脑")
        self.assertEqual(task2["price"], "8000")
        self.assertEqual(task2["category"], "学习")
        self.assertEqual(task2["status"], 2)
        self.assertEqual(task2["pic"],
                         "https://763850.iterator-traits.com" +
                         "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")
        self.assertEqual(task2["collect_num"], 1)
        self.assertEqual(task2["comment_num"], 0)

        self.assertEqual(task1["pic"],
                         "https://763850.iterator-traits.com/showimage" +
                         "/home/ubuntu/QingXian/media/picture/test.png")
        self.assertEqual(task1["price"], "面议")

        # 除了价格的表述，其余的各个键值对取法相同
        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['task_list']
        self.assertEqual(len(data_list), 2)
        task1 = data_list[0]
        task2 = data_list[1]
        self.assertEqual(task1["price"], "不高于59元/场")
        self.assertEqual(task2["price"], "无价位要求")

        # 无收藏
        request_dict = {"skey": "654321",
                        "goods_or_activity": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['task_list']
        self.assertEqual(len(data_list), 0)

        request_dict = {"skey": "654321",
                        "goods_or_activity": 1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['task_list']
        self.assertEqual(len(data_list), 0)

    # 测试不合法的skey输入
    def test_invalid_skey_request(self):
        request_dict = {"skey": "2333",
                        "goods_or_activity": 1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)
        # 测试无skey输入
        request_dict = {"goods_or_activity": 1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 错误goods_or_activity测试
    def test_invalid_goods_or_activity_request(self):
        request_dict = {"skey": "222",
                        "goods_or_activity": -1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"skey": "222",
                        "goods_or_activity": 2,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 无效page测试
    def test_invalid_page_request(self):
        request_dict = {"skey": "222",
                        "goods_or_activity": 0,
                        "page": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(len(response_json['task_list']), 0)

        request_dict = {"skey": "222",
                        "goods_or_activity": 1,
                        "page": 2}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(len(response_json['task_list']), 0)


# 测试我的发布任务
class GetMyCollectionTest(TestCase):
    def setUp(self):
        user = User.objects.create(open_id="222",
                                    skey="222",
                                    nickname="1",
                                    contact_info="18800123333",
                                    avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")

        task2 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=0,
                                    label="出售",
                                    category="学习",
                                    title="出售笔记本电脑",
                                    detail="出售苹果电脑",
                                    price_for_goods=8000,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=1)

        task1 = Task.objects.create(user_id=user.id,
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
                               task_id=task1.id,
                               feedback_id=-1)

        task3 = Task.objects.create(user_id=user.id,
                                    user_credit=100,
                                    goods_or_activity=1,
                                    label="休闲娱乐",
                                    category="休闲娱乐",
                                    title="一起看电影",
                                    detail="找朋友一起看电影",
                                    price_for_goods=-1,
                                    price_for_activity="不高于59元/场",
                                    contact_msg="请加我的微信",
                                    status=0)

        task4 = Task.objects.create(user_id=user.id,
                                    user_credit=96,
                                    goods_or_activity=1,
                                    label="失物招领",
                                    category="失物招领",
                                    title="捡到笔记本",
                                    detail="捡到笔记本电脑",
                                    price_for_goods=-1,
                                    price_for_activity="",
                                    contact_msg="请加我的微信",
                                    status=2)

        self.request_url = "/userpage/user/my_task"

    # 正确输入测试
    def test_proper_request(self):
        request_dict = {"skey": "222",
                        "status": 1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['task_list']
        self.assertEqual(len(data_list), 2)
        task1 = data_list[0]
        task2 = data_list[1]
        self.assertEqual(task2["label"], "出售")
        self.assertEqual(task2["goods_or_activity"], 0)
        self.assertEqual(task2["title"], "出售笔记本电脑")
        self.assertEqual(task2["price"], "8000")
        self.assertEqual(task2["category"], "学习")
        self.assertEqual(task2["collect_num"], 0)
        self.assertEqual(task2["comment_num"], 0)

        self.assertEqual(task1["pic"],
                         "https://763850.iterator-traits.com/showimage" +
                         "/home/ubuntu/QingXian/media/picture/test.png")
        self.assertEqual(task1["price"], "面议")

        # 除了价格的表述，其余的各个键值对取法相同
        request_dict = {"skey": "222",
                        "status": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['task_list']
        self.assertEqual(len(data_list), 1)
        task1 = data_list[0]
        self.assertEqual(task1["price"], "不高于59元/场")

        request_dict = {"skey": "222",
                        "status": 2,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['task_list']
        self.assertEqual(len(data_list), 1)
        task1 = data_list[0]
        self.assertEqual(task1["price"], "无价位要求")

        # 无发布任务
        user = User.objects.create(open_id="654321",
                                   skey="654321",
                                   nickname="2",
                                   contact_info="18800333333",
                                   avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")

        request_dict = {"skey": "654321",
                        "status": 0,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['task_list']
        self.assertEqual(len(data_list), 0)

        request_dict = {"skey": "654321",
                        "status": 1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['task_list']
        self.assertEqual(len(data_list), 0)

        request_dict = {"skey": "654321",
                        "status": 2,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        data_list = response_json['task_list']
        self.assertEqual(len(data_list), 0)

    # 测试不合法的skey输入
    def test_invalid_skey_request(self):
        request_dict = {"skey": "2333",
                        "status": 1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)
        # 测试无skey输入
        request_dict = {"status": 1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 错误status测试
    def test_invalid_goods_or_activity_request(self):
        request_dict = {"skey": "222",
                        "status": -1,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

        request_dict = {"skey": "222",
                        "status": 3,
                        "page": 1}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)

    # 无效page测试
    def test_invalid_page_request(self):
        request_dict = {"skey": "222",
                        "status": 0,
                        "page": 0}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(len(response_json['task_list']), 0)

        request_dict = {"skey": "222",
                        "status": 1,
                        "page": 2}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        self.assertEqual(len(response_json['task_list']), 0)


# 测试反馈
class FeedbackTest(TestCase):
    def setUp(self):
        user = User.objects.create(open_id="222",
                                   skey="222",
                                   nickname="1",
                                   contact_info="18800123333",
                                   avatar_url=str(SITE_DOMAIN).rstrip("/") + "/showimage/home/ubuntu/QingXian/media/picture/default_image.png")

        self.request_url = "/userpage/user/feedback"

    # 正确输入测试
    def test_proper_request(self):
        request_dict = {"skey": "222",
                        "detail": "反馈",
                        "pics": ""}
        user = User.objects.get(skey="222")
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        feedback_list = Feedback.objects.all()
        self.assertEqual(len(feedback_list), 1)
        feedback = feedback_list[0]
        self.assertEqual(feedback.user_id, user.id)
        self.assertEqual(feedback.detail, "反馈")
        self.assertEqual(Picture.objects.all().count(), 0)

        # 带图反馈
        request_dict = {"skey": "222",
                        "detail": "反馈2",
                        "pics": ["/home/ubuntu/QingXian/media/picture/test.png"]}
        user = User.objects.get(skey="222")
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 0)
        feedback_list = Feedback.objects.all()
        self.assertEqual(len(feedback_list), 2)
        feedback = feedback_list[1]
        self.assertEqual(Picture.objects.all().count(), 1)
        picture = Picture.objects.all()[0]
        self.assertEqual(picture.feedback_id, feedback.id)


    # 测试不合法的skey输入
    def test_invalid_skey_request(self):
        request_dict = {"skey": "2333",
                        "detail": "反馈",
                        "pics": ""}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)
        # 测试无skey输入
        request_dict = {"detail": "反馈",
                        "pics": ""}
        response_json = json.loads(self.client.post(self.request_url, request_dict, secure=True).content.decode())
        error = response_json['error']
        self.assertEqual(error, 1)