import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject, 
            '', 
            settings.EMAIL_HOST_USER, 
            [self.email], 
            fail_silently=self.fail_silently,
            html_message=self.text
        )



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


    def send_mail(self):
        # 发送邮件通知
        if self.parent is None:
            # 是评论我的博客
            # 发送邮件
            subject = "有人评论你的博客" 
            email = self.content_object.get_email()
        else:
            # 是回复评论
            subject = "有人回复你的评论"
            # 发送评论内容和对应博客链接
            email = self.reply_to.email
        
        if email != '':
            # 发送评论内容和对应博客链接
            # text = ' %s\n<a href="%s">%s</a> '%(self.text, self.content_object.get_url(), '点击查看')
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            text = render_to_string('comment/send_mail.html', context)
            send_mail = SendMail(subject, text, email)
            send_mail.start()


    def __str__(self):
        return self.text


    class Meta:
        ordering = ['comment_time']



