from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.http import JsonResponse
from .models import Comment
from .forms import CommentForm


# Create your views here.
def update_comment(request):
    
    # # 获取登陆之前的页面链接,如果获取不到返回首页,reverse()反向回去上一级
    # referer = request.META.get('HTTP_REFERER', reverse('home'))

    # # 数据检测
    # if not request.user.is_authenticated:
    #     return render(request, 'error.html',{'message': '用户未登录', 'redirect_to': referer})
    # # 去掉多余空格
    # text = request.POST.get('text', '').strip()
    # if text == '':
    #     return render(request, 'error.html',{'message': '评论内容为空', 'redirect_to': referer})
    # try:
    #     content_type = request.POST.get('content_type', '')
    #     object_id = int(request.POST.get('object_id', ''))
    #     # 利用contenttype得到相关联的模型，model_class()方法得到具体的模型
    #     model_class = ContentType.objects.get(model=content_type).model_class()
    #     # 根据具体的模型得到具体的对象
    #     model_obj = model_class.objects.get(pk=object_id)
    # except Exception as e:
    #     return render(request, 'error.html',{'message': '评论对象不存在', 'redirect_to': referer})

    # # 检测通过，保存数据
    # comment = Comment()
    # comment.user = request.user
    # comment.text = text
    # # 具体博客对象content_object
    # # Blog.objects.get(pk=object_id)  第一种方法，直接导入博客类，但是有局限性，因为评论可以不止评论博客
    # comment.content_object = model_obj
    # comment.save()

    
    # # 重定向，跳转回原来页面
    # return redirect(referer)
    
    data = {}
    # 获取登陆之前的页面链接,如果获取不到返回首页,reverse()反向回去上一级
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    # 实例化
    comment_form = CommentForm(request.POST, user=request.user)
    # 验证数据
    if comment_form.is_valid():
        # 检测通过，保存数据
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        # 具体博客对象content_object
        # Blog.objects.get(pk=object_id)  第一种方法，直接导入博客类，但是有局限性，因为评论可以不止评论博客
        comment.content_object = comment_form.cleaned_data['content_object']

        parent = comment_form.cleaned_data['parent']
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()


        # # 发送邮件
        # comment.send_mail()


        # 重定向，跳转回原来页面
        # return redirect(referer)

        # 返回数据
        data["status"] = 'SUCCESS'
        data["username"] = comment.user.get_nickname_or_username()
        data['content_type'] = ContentType.objects.get_for_model(comment).model
        # 返回本地时间,
        # data["comment_time"] = comment.comment_time.strftime("%Y-%m-%d %H:%M:%S")
        data['comment_time'] = comment.comment_time.timestamp()
        data["text"] = comment.text
        if not parent is None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''
    else:
        # return render(request, 'error.html',{'message': comment_form.errors, 'redirect_to': referer})
        # 返回数据
        data["status"] = 'ERROR'
        data["message"] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)




