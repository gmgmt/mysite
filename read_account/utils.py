import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail


def read_account_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    # key是cookie的get方法的第一个参数，ct.model是模型的字符串名称，
    key = "%s_%s_read"%(ct.model, obj.pk)
    if not request.COOKIES.get(key):
            # 总阅读数+1，get_or_create()方法，返回元祖，查找对象，查找到了返回true,找不到创建返回true
            readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
            readnum.read_num += 1
            readnum.save()

            # 当天阅读数+1
            date = timezone.now().date()
            readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
            readDetail.read_num += 1
            readDetail.save()
    return key


def get_seven_read_detail(content_type):
    today = timezone.now().date()
    read_nums = []
    dates = []
    for i in range(7,0,-1):
        date = today - datetime.timedelta(days=i)
        # 显示月和日
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        # 聚合，把所有阅读数合并
        result = read_details.aggregate(read_num_sum=Sum('read_num'))['read_num_sum']
        # 逻辑判断，如果result不为空取result，为空取0
        read_nums.append(result or 0)
    return dates, read_nums



def get_today_hot_data(content_type):
    # 获得今天的时间
    today = timezone.now().date()
    # 筛选今天的时间的阅读明细并排序
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
    #   显示前7条
    return read_details[:7]


def get_yesterday_hot_data(content_type):
    # 获得今天的时间
    today = timezone.now().date()
    # 获得昨天的时间
    yesterday = today - datetime.timedelta(days=1)
    # 筛选今天的时间的阅读明细并排序
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
    #   显示前7条
    return read_details[:7]




