from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User


# Create your models here.
class LikeCount(models.Model):
    '''关联contenttype外键，就相当于可以评论任何模型'''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='Likecount')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


    liked_num = models.IntegerField(default=0)


class LikeRecord(models.Model):
    '''记录谁对那个对象点赞'''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


    # 关联django自带的用户系统
    user = models.ForeignKey(User, related_name='Likerecord', on_delete=models.CASCADE)
    # 点赞日期
    liked_time = models.DateTimeField(auto_now_add=True)