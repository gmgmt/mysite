from django.shortcuts import render,get_object_or_404
from django.db.models import Count
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from .models import Blog,BlogType
# from comment.models import Comment
from read_account.utils import read_account_once_read
# from comment.forms import CommentForm
from user.forms import LoginForm



def get_blog_list_common_data(request, blogs_all_list):
    # 每十篇文章进行分页
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    # 获取页码参数（GET请求）
    page_num = request.GET.get('page', 1)
    page_of_blogs = paginator.get_page(page_num)
    # 获取当前页码
    current_page_num = page_of_blogs.number
    #  列表页面显示前后5页
    page_range = [x for x in range(int(page_num)-2, int(page_num)+3) if 0 < x <= paginator.num_pages]
    # 加上省略标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    '''
    # 获取博客分类对应的博客数量，一共两种方法
    # 第一种：Count方法需要一个字符串，统计的字段，因为BlogType和Blog有外键关联，所以写Blog小写就行了，用的时候再放入内存
    BlogType.objects.annotate(blog_count=Count('blog')) 
    # 第二种
    blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
        # 为blog_type添加blog_count属性
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)
    '''

    # 获取日期归档对应的博客数量，一共两种方法
    blog_dates = Blog.objects.dates('create_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year, 
                                         create_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count


    context = {}
    context['page_range'] = page_range
    context['page_of_blogs'] = page_of_blogs
    context['blogs'] = page_of_blogs.object_list
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    # dates(字段，类型，排序) 类型：年月日  ASC顺序 DESC倒序
    context['blog_dates'] = blog_dates_dict
    return context



def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    # 得到全部列表
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_type'] = blog_type
    return render(request, "blog/blogs_with_type.html", context)



def blogs_with_date(request, year, month):
    # 得到全部列表
    blogs_all_list = Blog.objects.filter(create_time__year=year, create_time__month=month)
    context = get_blog_list_common_data(request, blogs_all_list)

    context['blogs_with_date'] = "%s年%s月" % (year, month)
    return render(request, "blog/blogs_with_date.html", context)



def blog_list(request):
    # 得到全部列表
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)
    return render(request, "blog/blog_list.html", context)



def blog_detail(request, blog_pk):# blog_pk  主键
    context = {}
    blog = get_object_or_404(Blog, id=blog_pk)
    read_cookie_key = read_account_once_read(request, blog)

    # 通过contenttype获得关联的评论模型
    # blog_content_type = ContentType.objects.get_for_model(blog)
    # 筛选出具体哪条博客,parent=None代表是第一级评论
    # comments = Comment.objects.filter(content_type=blog_content_type, 
    #                                   object_id=blog.pk, parent=None)

    '''第二种方法
    if not request.COOKIES.get("blog_%s_readed" % blog_pk):
        if ReadNum.objects.filter(blog=blog).count():
            # 存在记录
            readnum = ReadNum.objects.get(blog=blog)

        else:
            # 不存在记录
            readnum = ReadNum(blog=blog)
        # 计数+1
        readnum.read_num += 1
        readnum.save()'''




    # 找到该博客的上一篇博客，通过时间排序，所以找到比他大（晚）__gt  的时间，是个集合，拿到最后一个就是上一个：
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    # 找到该博客的下一篇博客，通过时间排序，所以找到比他小（早）__lt  的时间，是个集合，拿到第一个就是上一个：
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context['blog'] = blog
    # context['comments'] = comments.order_by('-comment_time')
    # context['comment_count'] = Comment.objects.filter(content_type=blog_content_type, 
    #                                   object_id=blog.pk).count()
    # data = {}
    # # .model得到模型的字符串形式,初始化模型
    # data['content_type'] = blog_content_type.model
    # data['object_id'] = blog_pk
    # data['reply_comment_id'] = 0
    # context['comment_form'] = CommentForm(initial=data)
    response = render(request, "blog/blog_detail.html", context)
    # 第一个参数，key，第二个参数vaule，第三个参数max_age多长时间内有效（s为单位）第四个参数expires指定一个时间
    response.set_cookie(read_cookie_key, 'true') # 阅读cookie标记
    return response