from django.db import models
import django.utils.timezone as timezone
# Create your models here.

# 用户表
class User(models.Model):
    open_id = models.CharField(max_length=64, unique=True, db_index=True)
    username = models.CharField(max_length=32, unique=True)
    skey = models.CharField(max_length=256)
    contact_info = models.CharField(max_length=256)
    credit = models.IntegerField()
    objects = models.Manager()

# 二手商品表
class Good(models.Model):
    user_id = models.IntegerField()
    title = models.CharField(max_length=256)
    detail = models.TextField()
    category = models.CharField(max_length=256)
    # 出售为0，求购为1
    sale_or_require = models.IntegerField()
    # -1为面议
    price = models.FloatField()
    submit_time = models.DateTimeField(default=timezone.now)
    release_time = models.DateTimeField(default=timezone.now)
    contact_msg = models.TextField()
    # 发布状态（0：待审核，1：已审核，上架，2：下架）
    status = models.IntegerField()
    user_credit = models.IntegerField(default=100)
    objects = models.Manager()

# 消息活动
class Activity(models.Model):
    user_id = models.IntegerField()
    # 有个标签位置
    label = models.CharField(max_length=256, default="其它")
    title = models.CharField(max_length=256)
    detail = models.TextField()
    category = models.CharField(max_length=256)
    price_req = models.IntegerField()
    price = models.CharField(max_length=256)
    submit_time = models.DateTimeField(default=timezone.now)
    release_time = models.DateTimeField(default=timezone.now)
    contact_msg = models.TextField()
    status = models.IntegerField()
    user_credit = models.IntegerField(default=100)
    objects = models.Manager()

# 评论
class Comment(models.Model):
    reviewer_id = models.IntegerField()
    reciever_id = models.IntegerField()
    category = models.IntegerField()
    good_id = models.IntegerField()
    activity_id = models.IntegerField()
    detail = models.TextField()
    release_time = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

# 图片
class Picture(models.Model):
    picture_url = models.CharField(max_length=256)
    pic_count = models.IntegerField()
    category = models.IntegerField()
    good_id = models.IntegerField()
    activity_id = models.IntegerField()
    user_id = models.IntegerField()
    feedback_id = models.IntegerField()
    objects = models.Manager()

# 收藏
class Collection(models.Model):
    user_id = models.IntegerField()
    category = models.IntegerField()
    good_id = models.IntegerField()
    activity_id = models.IntegerField()
    release_time = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

# 反馈
class Feedback(models.Model):
    user_id = models.IntegerField()
    detail = models.TextField()
    release_time = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

# 提醒
class Reminder(models.Model):
    reciever_id = models.IntegerField()
    category = models.IntegerField()
    comment_id = models.IntegerField()
    title = models.TextField()
    detail = models.TextField()
    release_time = models.DateTimeField(default=timezone.now)
    objects = models.Manager()