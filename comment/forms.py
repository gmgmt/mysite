from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from ckeditor.widgets import CKEditorWidget
from .models import Comment


class CommentForm(forms.Form):
    # 类型,widget=forms.HiddenInput,不显示
    content_type = forms.CharField(widget=forms.HiddenInput)
    # 数字类型
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=CKEditorWidget(config_name="comment_ckeditor"), 
                           label=False,
                           error_messages = {'required': '评论内容不能为空'})
    reply_comment_id = forms.IntegerField(widget=forms.
                                           HiddenInput(attrs={'id': 'reply_comment_id'}))


    def __init__(self, *args, **kwargs):
        '''将user传入'''
        if 'user' in kwargs:
            # 首先初始化不一定传入user参数，所以用get，其次默认并没有user参数，如果有他会报错，所以得把它pop出来给self.user
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)



    def clean(self):
        # 判断用户是否登陆：
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登陆')

        # 评论对象验证
        content_type = self.cleaned_data['content_type']
        object_id = self.cleaned_data['object_id']
        try:
            # 查看是否有对应类型
            model_class = ContentType.objects.get(model=content_type).model_class()
            # 去除对应的对象
            model_obj = model_class.objects.get(id=object_id)
            # 验证通过，写入cleaned_data，方便后面views.py中的函数的调用
            self.cleaned_data['content_object'] = model_obj
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论对象不存在')
        return self.cleaned_data



    def clean_reply_comment_id(self):
        '''验证'''
        reply_comment_id = self.cleaned_data['reply_comment_id']
        if reply_comment_id < 0:
            raise forms.ValidationError('回复出错')
        elif reply_comment_id == 0:
            self.cleaned_data['parent'] = None
        elif Comment.objects.filter(pk=reply_comment_id).exists():
            self.cleaned_data['parent'] = Comment.objects.get(pk=reply_comment_id)
        else:
            raise forms.ValidationError('回复出错')
        return reply_comment_id

