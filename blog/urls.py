from django.conf.urls import url
from blog import views
urlpatterns = [

    url(r'^upload', views.upload),
    url(r'^delArticle/(?P<article_id>\d+)', views.delArticle),
    url(r'^addArticle', views.addArticle),
    url(r'^comment_up_down', views.comment_up_down),
    url(r'^article_comment', views.article_comment),
    url(r'^article_up', views.article_up),
    url(r'^comment_tree/(?P<article_id>\d+)', views.comment_tree),
    url(r'^tag', views.tag),
    url(r'^category', views.category),
    url(r'^manage', views.manage),
    url(r'^(?P<username>.*)/article/(?P<article_id>.*)', views.article_detail),
    url(r'^(?P<username>.*)/(?P<field>(tag|category|date))/(?P<field_name>.*)', views.homesite),
    url(r'^(?P<username>.*)', views.homesite),



   ]