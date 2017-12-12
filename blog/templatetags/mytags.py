from django.template import Library

register=Library()

@register.filter
def filter_time(create_time):

    import datetime

    now_time=datetime.datetime.now()
    create_time=datetime.datetime(year=create_time.year,month=create_time.month,
        day=create_time.day,hour=create_time.hour,minute=create_time.minute,second=create_time.second)

    ret=str(now_time -  create_time)
    if "," not in ret:
        h,m,_=ret.split(":")
        ret="%s小时%s分钟"%(h,m)
        return ret
    ret,_=ret.split(",")
    t,_=ret.split(" ")
    time=""
    if int(t)>30:
        t1=int(t)/30
        if t1>12:
            t2=t1/12
            year,month=str(t2).split(".")
            time="%s年%s个月"%(year,month[0])
        else:
            month,day=str(t1).split(".")
            time="%s月"%(month)
    else:
        time="%s天"%(t)




    return time