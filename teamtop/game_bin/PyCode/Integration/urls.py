#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# Django路径
# 按照目录，自动生成访问的uri和索引目录
#===============================================================================
from django.conf.urls import defaults
from Integration import settings, AutoURL

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


# 构建正在的路径列表
lis = ['',
	# 索引页
	(r'^$', "Integration.WebPage.Index.Index"),
	(r'^model', "Integration.WebPage.model.me.get"),
	(r'^serve/', "Integration.WebPage.pf.s.get"),
	(r'^pf/', "Integration.WebPage.pf.s.get"),
	# 静态文件
	(r'^site_medias/(?P<path>.*)$','django.views.static.serve', {'document_root':settings.STATICFILES_DIRS, 'show_indexes': True}),
	]
lis.extend(AutoURL.auto_patterns.items())
urlpatterns = defaults.patterns(*lis)

