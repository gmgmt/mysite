from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from ckeditor_uploader.fields import RichTextUploadingField
from read_account.models import ReadNumExpendMethod, ReadDetail
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse





#    博客类型：一篇文章对应一种分类
class BlogType(models.Model):
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return self.type_name

class Blog(models.Model, ReadNumExpendMethod):
    #   标题
    title = models.CharField(max_length=50, verbose_name='标题')
    #   博客分类
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE, verbose_name='博客分类')
    #   内容， 富文本
    content = RichTextUploadingField()
    #   作者
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    #  可以通过该字段直接获取ReadDetail模型，该模型为ContentType外键模型
    read_details = GenericRelation(ReadDetail)
    
    #   创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    #   最后更新时间
    last_update_time = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')

    '''
    def get_read_num(self):
        try:
            return self.readnum.read_num
        except exceptions.ObjectDoesNotExist:
            return 0
    '''
    
    def get_url(self):
        return reverse('blog_detail', kwargs={'blog_pk': self.pk})

    def get_user(self):
        return self.author


    def get_email(self):
        return self.author.email    


    def __str__(self):
        return "<Blog： %s>"%self.title


    class Meta:
        ordering = ['-create_time']


'''
class ReadNum(models.Model):
    #   添加一个阅读次数字段
    read_num = models.IntegerField(default=0)
    blog = models.OneToOneField(Blog, on_delete=models.CASCADE)
'''


