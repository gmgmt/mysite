from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Comment
from ..forms import CommentForm

register = template.Library()

@register.simple_tag
def get_comment_count(obj):
    # 得到模型类型
    content_type = ContentType.objects.get_for_model(obj)
    # 得到具体数量
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()

@register.simple_tag
def get_comment_form(obj):
    '''获取评论表单'''
    content_type = ContentType.objects.get_for_model(obj)
    data = {}
    # .model得到模型的字符串形式,初始化模型
    data['content_type'] = content_type.model
    data['object_id'] = obj.pk
    data['reply_comment_id'] = 0
    form = CommentForm(initial=data)
    return form


@register.simple_tag
def get_comment_list(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent=None)
    return comments.order_by('-comment_time')
