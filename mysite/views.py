import datetime

from django.utils import timezone
from django.db.models import Sum
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from read_account.utils import get_seven_read_detail, get_today_hot_data, get_yesterday_hot_data
from blog.models import Blog





def get_senven_days_hot_blogs():
    '''获取前7天的热门博客，可以修改为获取任一天'''
    # 获得今天的时间
    today = timezone.now().date()
    # 获得第前7天的时间
    date = today - datetime.timedelta(days=7)
    # 筛选今天的时间的阅读明细并排序,小于7天date__lt=date, 大于等于第前7天date__gte=date，
    # .values()以...分组,.annotate(read_num_sum=Sum('read_num'))求和
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date) \
                                      .values('id', 'title') \
                                      .annotate(read_num_sum=Sum('read_details__read_num')) \
                                      .order_by('-read_num_sum')
                                            
    #   显示前7条
    return blogs[:7]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates,read_nums = get_seven_read_detail(blog_content_type)
    # 获得今天的热门博客排行
    today_hot_data = get_today_hot_data(blog_content_type)
    # 获得昨天的热门博客排行
    yesterday_hot_data = get_yesterday_hot_data(blog_content_type)

    # 获取7天热门博客的缓存
    senven_days_hot_blogs = cache.get('senven_days_hot_blogs')
    if senven_days_hot_blogs is None:
        senven_days_hot_blogs = get_senven_days_hot_blogs()
        # 写到缓存,第一个参数键值，第二个参数缓存内容，第三个有效期,单位秒
        cache.set('senven_days_hot_blogs', senven_days_hot_blogs, 3600)



    context = {} 
    context['senven_days_hot_blogs'] = get_senven_days_hot_blogs
    context['yesterday_hot_data'] = yesterday_hot_data
    context['today_hot_data'] = today_hot_data
    context['dates'] = dates
    context['read_nums'] = read_nums
    return render(request, 'home.html', context)



