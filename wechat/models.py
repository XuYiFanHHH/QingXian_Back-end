from django.db import models
import django.utils.timezone as timezone
# Create your models here.

# 用户表
class User(models.Model):
    open_id = models.CharField(max_length=64, unique=True, db_index=True)
    nickname = models.CharField(max_length=32, unique=True)
    skey = models.CharField(max_length=256)
    avatar_url = models.CharField(max_length=256)
    credit = models.IntegerField(default=100)
    contact_info = models.CharField(max_length=256, default="")
    objects = models.Manager()

# 二手商品表
class Task(models.Model):
    user_id = models.IntegerField()
    user_credit = models.IntegerField(default=100)
    goods_or_activity = models.IntegerField()
    label = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    detail = models.TextField()
    category = models.CharField(max_length=256)
    # 商品的price（-1为面议）
    price_for_goods = models.IntegerField()
    # 信息共享有的会有价格要求
    price_for_activity = models.CharField(max_length=256)
    submit_time = models.DateTimeField(default=timezone.now)
    release_time = models.DateTimeField(default=timezone.now)
    contact_msg = models.TextField()
    # 发布状态（0：待审核，1：已审核，上架，2：下架）
    status = models.IntegerField()
    undercarriage_reason = models.CharField(max_length=256)
    objects = models.Manager()

# 评论
class Comment(models.Model):
    reviewer_id = models.IntegerField()
    receiver_id = models.IntegerField()
    task_id = models.IntegerField()
    detail = models.TextField()
    release_time = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

# 图片
class Picture(models.Model):
    picture_url = models.CharField(max_length=256)
    task_id = models.IntegerField()
    feedback_id = models.IntegerField()
    objects = models.Manager()

# 收藏
class Collection(models.Model):
    user_id = models.IntegerField()
    task_id = models.IntegerField()
    collect_time = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

# 反馈
class Feedback(models.Model):
    user_id = models.IntegerField()
    detail = models.TextField()
    release_time = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

# 提醒
class Notification(models.Model):
    reciever_id = models.IntegerField()
    category = models.IntegerField()
    comment_id = models.IntegerField()
    title = models.TextField()
    detail = models.TextField()
    release_time = models.DateTimeField(default=timezone.now)
    objects = models.Manager()