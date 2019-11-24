from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User




class Comment(models.Model):
    '''关联contenttype外键，就相当于可以评论任何模型'''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # 评论内容
    text = models.TextField()
    # 评论时间，评论时自动添加
    comment_time = models.DateTimeField(auto_now_add=True)
    # 关联django自带的用户系统
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)

    # 记录一条评论下的所有回复,related_name反向关联的名称
    root = models.ForeignKey('self', null=True, related_name='root_comment', 
                              on_delete=models.CASCADE)
    # 第一集可以为空，外键关联自己
    parent = models.ForeignKey('self', null=True, related_name='parent_comment',
                                on_delete=models.CASCADE)
    # 添加回复谁的字段
    reply_to = models.ForeignKey(User, null=True, related_name='replies', 
                                 on_delete=models.CASCADE)



    def __str__(self):
        return self.text

    def get_user(self):
        return self.user
    def get_url(self):
        return self.content_object.get_url()

    class Meta:
        ordering = ['comment_time']



