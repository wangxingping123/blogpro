import json,os
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.db.models import Count, F
from django.db import transaction
from django.conf import settings
from django.contrib import auth
from django.shortcuts import render, redirect, HttpResponse
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
# from blog import models
from blog.forms import *
from django.forms import ValidationError

# 滑动验证码插件
from blog.geetest import GeetestLib
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"
mobile_geetest_id = "7c25da6fe21944cfe507d2f9876775a9"
mobile_geetest_key = "f5883f4ee3bd4fa8caec67941de1b903"


def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)

def pcajax_validate(request):

    if request.method == "POST":

        data_dic = {"flag": False, "data": None}

        # if request.POST.get("valid").upper() != request.session["valid_str"].upper():
        #     form.add_error("valid", ValidationError("验证码错误"))

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        print("status",status)
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)

        if result:

            username=request.POST.get("username")
            password=request.POST.get("password")
            print(password,username)
            user=auth.authenticate(username=username,password=password)
            print(user)
            if user:
                auth.login(request, user)
                data_dic["flag"] = True
            else:
                data_dic["flag"]=False


        return HttpResponse(json.dumps(data_dic))


# Create your views here.
def login(request):
    return render(request, "login.html")

def logout(request):
    '''注销'''
    auth.logout(request)
    ret=redirect("/login/")
    ret.delete_cookie("prev_path")
    return ret

def register(request):
    if request.method == "POST":
        form = RegesterForm(request.POST)
        data_dic = {"flag": False, "errors": None}
        if form.is_valid():
            if request.FILES.get("portrair"):
                form.cleaned_data["avatar"] = request.FILES.get("portrair")
            form.cleaned_data.pop("password_repeat")
            user=models.UserInfo.objects.create_user(**form.cleaned_data)
            models.Blog.objects.create(title=user.username,site=user.username,theme=user.username,user=user)

            data_dic["flag"] = True
        data_dic["errors"] = form.errors

        return HttpResponse(json.dumps(data_dic))

    return render(request, "register.html")

def valid_color():
    '''返回随机颜色'''
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return color

def get_valid_code(request):
    '''获取随机验证码图片'''
    img = Image.new(mode="RGB", size=(170, 40), color=valid_color())  # 创建一张背景图片随机的图片
    draw = ImageDraw.Draw(img, mode="RGB")  # 给图片创建一个画笔
    font = ImageFont.truetype(font="blog/static/font/kumo.ttf", size=25)  # 创建字体
    valid_list = []
    for i in range(5):
        random_num = str(random.randint(0, 9))  # 产生随机的数字
        random_lower_letter = chr(random.randint(65, 90))  # 产生随机的小写字母
        random_upper_letter = chr(random.randint(97, 122))  # 产生随机的大写字母
        random_str = random.choice([random_num, random_lower_letter, random_upper_letter])  # 从以上的随机中产生一个随机字符
        draw.text(xy=[30 + i * 24, 10], text=random_str, fill=valid_color(), font=font)  # 在背景图片中写入随机字符
        valid_list.append(random_str)  # 将随机字符串保存到列表中
    for i in range(40):
        '''在图片中画如随机的点'''
        draw.point([random.randint(0, 170), random.randint(0, 40)], fill=valid_color())
    for i in range(5):
        '''在图片中画如随机的线'''
        draw.line((random.randint(0, 170), random.randint(0, 40), random.randint(0, 170), random.randint(0, 40)),
                  fill=valid_color())

    f = BytesIO()  # 在内存中创建一个文件对象
    img.save(f, "png")  # 将随机字符串的图片保存到文件中
    data = f.getvalue()  # 获取随机字符串图片的二进制
    valid_str = ''.join(valid_list)
    request.session["valid_str"] = valid_str  # 将图片中产生的随机字符串保存到session中
    return HttpResponse(data)

def index(request, *args, **kwargs):
    '''查询出首页要渲染的内容'''
    if kwargs:
        article_objs = models.Article.objects.filter(siteArticleCategory__name=kwargs.get("article_cate_name"))
    else:
        article_objs = models.Article.objects.all()
    site_cate_objs = models.SiteCategory.objects.all()
    return render(request, "index.html", {"site_cate_objs": site_cate_objs, "article_objs": article_objs})

def homesite(request, username, **kwargs):
    '''显示当前用户站点的内容，数据库的查询'''

    user = models.UserInfo.objects.filter(username=username).first()

    if not user:
        return render(request, "error404.html")
    article_list = user.article_set.all()

    # 当前博客的文章分类及文章数量
    # category_name_count=models.Category.objects.filter(blog=user.blog).annotate(article_count=Count("article__nid")).values_list("title","article_count")

    # 当前博客的标签名及它下面所在的文章数量
    # tag_name_count=models.Tag.objects.filter(blog=user.blog).annotate(article_count=Count("article__nid")).values_list("title","article_count")
    # print(tag_name_count)

    # 当前博客按月分类的月份及文章数量
    date_name_count = models.Article.objects.filter(user=user).extra(
        select={"filter_create_time": "strftime('%%Y/%%m',create_time)"}).values_list("filter_create_time").annotate(
        Count("nid"))
    # print(date_name_count)

    if kwargs:
        if kwargs.get("field") == "tag":
            article_list = user.article_set.filter(tags__title=kwargs.get("field_name"))
        elif kwargs.get("field") == "category":
            article_list = user.article_set.filter(category__title=kwargs.get("field_name"))
        elif kwargs.get("field") == "date":
            year, month = kwargs.get("field_name").split("/")
            article_list = user.article_set.filter(create_time__year=year, create_time__month=month)
        else:
            return render(request, "error404.html")
    return render(request, "homesite.html",
                  {"user": user, "date_name_count": date_name_count, "article_list": article_list})

def article_detail(request, username, article_id):
    '''渲染文章的详细内容'''
    if not article_id:
        return render(request, "error404.html")
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, "error404.html")
    date_name_count = models.Article.objects.filter(user=user).extra(
        select={"filter_create_time": "strftime('%%Y/%%m',create_time)"}).values_list("filter_create_time").annotate(
        Count("nid"))
    article = models.Article.objects.filter(nid=article_id).first()
    if not article:
        return render(request, "error404.html")
    #文章的所有评论

    obj= render(request, "article.html", {"user": user, "date_name_count": date_name_count, "article": article})
    obj.set_cookie("prev_path",request.path)
    return obj

def article_up(request):
    '''用户对文章的推荐或反对'''
    up_or_down = request.POST.get("up_or_down")
    user_id = request.user.nid
    article_id = int(request.POST.get("article_id"))
    data = {"flag": True, "point": None}
    try:
        if up_or_down == "推荐":
            with transaction.atomic():
                '''事务'''
                models.ArticleUp.objects.create(user_id=user_id, article_id=article_id, updown="推荐")
                models.Article.objects.filter(nid=article_id).update(up_count=F("up_count") + 1)
            data["point"] = "推荐成功"
        elif up_or_down == "反对":
            with transaction.atomic():
                '''事务'''
                models.ArticleUp.objects.create(user_id=user_id, article_id=article_id, updown="反对")
                models.Article.objects.filter(nid=article_id).update(up_count=F("up_count") + 1)
            data["point"] = "反对"
    except:
        if models.ArticleUp.objects.filter(user_id=user_id, article_id=article_id).first().updown == "推荐":
            data["flag"] = False
            data["point"] = "你已推荐过"
        elif models.ArticleUp.objects.filter(user_id=user_id, article_id=article_id).first().updown == "反对":
            data["flag"] = False
            data["point"] = "你已反对过"

    return HttpResponse(json.dumps(data))

def article_comment(request):
    '''对文章评论的处理'''
    username = request.user.username
    user_id = request.user.nid
    article_id = request.POST.get("article_id")
    comment_content = request.POST.get("comment_content")
    print(request.POST.get("parent_comment_id"))
    parent_comment_id=request.POST.get("parent_comment_id")
    data = {"username": None, "comment_content": None,"parent_comment_username":None}
    if parent_comment_id:      #如果是评论的评论
        with transaction.atomic():
            '''事务'''
            comment_obj=models.Comment.objects.create(user_id=user_id, article_id=article_id, content=comment_content,parent_comment_id=parent_comment_id)
            models.Article.objects.filter(nid=article_id).update(comment_count=F("comment_count") + 1)
            parent_comment_username=comment_obj.parent_comment.user.username
            data["parent_comment_username"]=parent_comment_username
    else:
        with transaction.atomic():
            '''事务'''
            models.Comment.objects.create(user_id=user_id, article_id=article_id, content=comment_content)
            models.Article.objects.filter(nid=article_id).update(comment_count=F("comment_count")+1)
    data["username"]=username
    data["comment_content"]=comment_content
    return HttpResponse(json.dumps(data))

def comment_up_down(request):
    # 给文章评论点推荐或反对：
    comment_id = int(request.POST.get("comment_id"))
    user_id = request.user.nid
    up_or_down = request.POST.get("up_or_down")[:2]
    data = {"flag": True, "point": None}
    try:
        if up_or_down == "推荐":
            with transaction.atomic():
                '''事务'''
                models.CommentUp.objects.create(user_id=user_id, comment_id=comment_id, updown="推荐")
                models.Comment.objects.filter(nid=comment_id).update(up_count=F("up_count") + 1)
            count = models.Comment.objects.filter(nid=comment_id).first().up_count
            data["count"] = '推荐(' + str(count) + ')'
            data["point"] = "推荐成功"

        elif up_or_down == "反对":
            with transaction.atomic():
                '''事务'''
                models.CommentUp.objects.create(user_id=user_id, comment_id=comment_id, updown="反对")
                models.Comment.objects.filter(nid=comment_id).update(up_count=F("up_count") + 1)
            data["point"] = "反对成功"
            count = models.Comment.objects.filter(nid=comment_id).first().up_count
            data["count"] = '反对(' + str(count) + ')'
    except:
        if models.CommentUp.objects.filter(user_id=user_id, comment_id=comment_id).first().updown == "推荐":
            data["flag"] = False
            data["point"] = "你已推荐过"
        elif models.CommentUp.objects.filter(user_id=user_id, comment_id=comment_id).first().updown == "反对":
            data["flag"] = False
            data["point"] = "你已反对过"

    return HttpResponse(json.dumps(data))

def manage(request):
    '''个人博客管理页面'''
    if not request.user.is_authenticated():
        return redirect("/login/")
    articles_obj=request.user.article_set.all()
    category_obj=request.user.blog.category_set.all()
    tags_obj = request.user.blog.tag_set.all()
    #分页
    paginator=Paginator(articles_obj,10) #实例化一个分页器对象
    page = request.GET.get('page', 1)
    currentPage = int(page)


    try:
        articles_obj = paginator.page(page)
    except PageNotAnInteger:
        articles_obj = paginator.page(1)
    except EmptyPage:
        articles_obj = paginator.page(paginator.num_pages)

    return render(request,"manage.html",locals())

def comment_tree(request,article_id):
    '''生产评论树状的数据类型'''
    article = models.Article.objects.filter(nid=article_id).first()
    comment_dic = {}
    comment_tree=[]
    for comment in article.comment_set.all():
        comment_dic[comment.nid] = {"id": comment.nid, "content": comment.content,
                                    "create_time": str(comment.create_time)[0:19], "username": comment.user.username,
                                    "user_avatar":str(comment.user.avatar),
                                    "down_count": comment.down_count,
                                    "parent_comment_id": comment.parent_comment_id,
                                    "children_list": []}
    for item in comment_dic.values():
        if item["parent_comment_id"]:
            comment_dic[item["parent_comment_id"]]["children_list"].append(item)
        else:
            comment_tree.append(item)

    return HttpResponse(json.dumps(comment_tree))

def category(request):
    if not request.user:
        return render(request,"error404.html")
    blog=request.user.blog
    category_obj=models.Category.objects.filter(blog=request.user.blog)
    tags_obj=models.Tag.objects.filter(blog=blog)
    return render(request,"category.html",{"category_obj":category_obj,"tags_obj":tags_obj})

def tag(request):
    if not request.user:
        return render(request,"error404.html")
    blog = request.user.blog
    category_obj = models.Category.objects.filter(blog=blog)
    tags_obj = models.Tag.objects.filter(blog=blog)
    return render(request, "tag.html", {"category_obj": category_obj, "tags_obj": tags_obj})

def addArticle(request):
    '''添加文章'''
    if request.method=="POST":
        forms=ArticleForm(request.POST)
        if forms.is_valid():
            title=forms.cleaned_data.get("article_title")
            content=forms.cleaned_data.get("article_content")
            personal_category=request.POST.get("personal_category")#获取个人分类id
            site_category=request.POST.get("site_category") #获取站点分类id
            taglist=request.POST.getlist("personal_tag")
            article_obj=models.Article.objects.create(title=title,desc=content[0:50],user=request.user,category_id=personal_category,siteArticleCategory_id=site_category)
            models.ArticleDetail.objects.create(content=content,article=article_obj)

            if taglist:
                for tag_id in taglist:
                    models.Article2Tag.objects.create(article_id=article_obj.nid,tag_id=tag_id)

            return render(request,"ArticleDone.html",{"article_obj":article_obj})

        else:

            return render(request,"addArticle.html",{"forms":forms})
    personal_category=models.Category.objects.filter(blog=request.user.blog)
    SiteCategory=models.SiteCategory.objects.all()
    personal_tag=models.Tag.objects.filter(blog=request.user.blog)
    return render(request,"addArticle.html",locals())

def delArticle(request,article_id):
    # 删除文章
    data={"flag":True}
    try:
        with transaction.atomic():
            models.Article.objects.filter(nid=article_id).delete()
            models.ArticleDetail.objects.filter(article_id=article_id)
    except:
        data["flag"]=False
    return HttpResponse(json.dumps(data))

def upload(request):
    '''写文章是图片的上传'''
    img_obj=request.FILES.get("imgFile")
    path=os.path.join(settings.MEDIA_ROOT,"articleLoads",img_obj.name)
    with open(path,"wb")as f:
        for i in img_obj:
            f.write(i)

    data={
        "error": 0,
        "url": "/media/articleLoads/"+img_obj.name+""
    }

    return HttpResponse(json.dumps(data))
