from django.db import models
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):  # settings:   AUTH_USER_MODEL = "blog.UserInfo"
    """
    用户信息
    """
    nid = models.BigAutoField(primary_key=True)
    nickname = models.CharField(verbose_name='昵称', max_length=32)
    telephone = models.CharField(max_length=11, blank=True, null=True, unique=True, verbose_name='手机号码')
    avatar = models.FileField(verbose_name='头像', upload_to='avatar', default="/avatar/default.png")
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)

    def __str__(self):
        return self.username


class Blog(models.Model):
    """
    站点信息
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site = models.CharField(verbose_name='个人博客后缀', max_length=32, unique=True)
    theme = models.CharField(verbose_name='博客主题', max_length=32)

    user = models.OneToOneField(to='UserInfo', to_field='nid')

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'category'
        ordering = ['title']


class Article(models.Model):
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章描述')
    read_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    siteArticleCategory=models.ForeignKey(verbose_name="站点文章类型",to="SiteArticleCategory",null=True)
    category = models.ForeignKey(verbose_name='文章类型', to='Category', to_field='nid', null=True)
    user = models.ForeignKey(verbose_name='所属用户', to='UserInfo', to_field='nid')
    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )

    def __str__(self):
        return self.title


class ArticleDetail(models.Model):
    """
    文章详细表
    """
    nid = models.AutoField(primary_key=True)
    content = models.TextField(verbose_name='文章内容', )

    article = models.OneToOneField(verbose_name='所属文章', to='Article', to_field='nid')

    def __str__(self):
        return self.article.title

class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)

    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)

    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid')
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid')

    parent_comment = models.ForeignKey('self', blank=True, null=True, verbose_name='父级评论')

    def __str__(self):
        return self.content


class CommentUp(models.Model):
    """
    评论支持/反对表
    """

    nid = models.AutoField(primary_key=True)
    updown = models.CharField(verbose_name="反对还是支持", max_length=16)
    user = models.ForeignKey('UserInfo', null=True)
    comment = models.ForeignKey("Comment", null=True)

    class Meta:
        unique_together = [
            ('comment', 'user'),
        ]


class ArticleUp(models.Model):
    """
    文章支持/反对表
    """
    nid = models.AutoField(primary_key=True)
    updown=models.CharField(verbose_name="反对还是支持",max_length=16)
    user = models.ForeignKey('UserInfo', null=True)
    article = models.ForeignKey("Article", null=True)

    class Meta:
        unique_together = [
            ('article', 'user'),
        ]


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid')
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid')

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]

class SiteCategory(models.Model):
    '''主分类表'''
    name=models.CharField(verbose_name="主分类名",max_length=32)
    def __str__(self):
        return self.name

class SiteArticleCategory(models.Model):
    '''站点文章分类表'''
    name=models.CharField(verbose_name="文章分类名",max_length=32)
    siteCategory=models.ForeignKey(to="SiteCategory")

    def __str__(self):
        return self.name