from django.forms import Form,fields,widgets,ValidationError
from blog import models
from blog.plogins import xssplogin

class LoginForm(Form):
    '''创建登录规则'''
    username=fields.CharField(required=True,error_messages={"required":"用户名不能为空"})
    password=fields.CharField(required=True,error_messages={"required":"密码不能为空"})
    valid=fields.CharField(required=True,error_messages={"required":"请输入验证码"})

class RegesterForm(Form):
    '''创建注册页面的字段的规则'''
    username=fields.CharField(min_length=4,error_messages={"required":"用户名不能为空","min_length":"用户名不能小于四位"})
    password=fields.CharField(min_length=8,error_messages={"required":"密码不能为空","min_length":"密码不能少于八位"})
    password_repeat=fields.CharField(min_length=8,error_messages={"required":"密码不能为空","min_length":"密码不能少于八位"})
    email=fields.EmailField(error_messages={"required":"邮箱不能为空",'invalid': '邮箱格式不正确',})
    def clean_username(self):
        username=self.cleaned_data.get("username")
        if models.UserInfo.objects.filter(username=username):
            self.add_error("username",ValidationError("该用户名已被注册"))
        return username
    def clean(self):
        pwd=self.cleaned_data.get("password")
        pwd_repeat=self.cleaned_data.get("password_repeat")
        if pwd != pwd_repeat:
            self.add_error("password_repeat",ValidationError("两次密码输入不一致"))
        return self.cleaned_data

class ArticleForm(Form):

    article_title=fields.CharField(max_length=32,error_messages={"required":"标题不能为空",
                            "max_length":"标题不能超过32位"})
    article_content=fields.CharField(error_messages={"required":"文章内容不能为空"})

    def clean_article_content(self):
        content=self.cleaned_data.get("article_content")
        self.cleaned_data["article_content"]=xssplogin.filter_xss(content)
        return self.cleaned_data["article_content"]