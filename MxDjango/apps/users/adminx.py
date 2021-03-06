# _*_ coding:utf-8 _*_
__author__ = 'zhuzhao'
__date__ = '2017/5/15 16:27'
import xadmin
from xadmin import views
from .models import EmailVerifyRecord,Banner


# ----- adminx 全局配置
class BaseSetting(object):
    enable_themes = True
    use_booswatch = True


class GlobalSettings():
    site_title = '慕学后台管理系统'
    site_footer = '慕学在线网'
    menu_style = 'accordion'
# ------

class EmailVerifyRecordAdmin(object):

    list_display = ['code','email','send_type','send_time']  #后台自定义显示列
    search_fields = ['code','email','send_type'] #定义后台搜索
    list_filter = ['code','email','send_type','send_time'] #通过时间搜索


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time'] #后台自定义显示列 显示字段
    search_fields = ['title', 'image', 'url', 'index'] #定义后台搜索 搜索功能
    list_filter = ['title', 'image', 'url', 'index', 'add_time'] #过滤器 通过时间搜索

xadmin.site.register(EmailVerifyRecord,EmailVerifyRecordAdmin)
xadmin.site.register(Banner,BannerAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)