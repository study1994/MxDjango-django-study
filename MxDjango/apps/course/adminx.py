# -*- coding: utf-8 -*-

import xadmin

from .models import Course, Lesson, Video, CourseResource,BannerCourse


class LessionInline(object):
    model = Lesson
    extra = 0


class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums','add_time','get_zj_nums','go_to']     # 显示字段
    search_fields = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image','click_nums']                  # 搜索功能
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums','add_time']      # 过滤器
    ordering = ['-click_nums']                               # 默认排序
    readonly_fields = ['click_nums','add_time']             # 只读
    exclude = ['fav_nums']                                    # 该字段不展示
    inlines = [LessionInline]                              # 同一个model注册两个管理器
    style_fields = {'detail':'ueditor'}                # 看xadmin/plugins/ueditor
    import_excel = True                                    # 看xadmin/plugins/excel

    def queryset(self):
        qs = super(CourseAdmin,self).queryset()
        qs = qs.filter(is_banner=False)
        return qs

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            pass
        return super(CourseAdmin, self).post(request, args, kwargs)



class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums','add_time']     # 显示字段
    search_fields = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image','click_nums']                  # 搜索功能
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums','add_time']      # 过滤器
    ordering = ['-click_nums']                               # 默认排序
    readonly_fields = ['click_nums','add_time']             # 只读
    exclude = ['fav_nums']                                    # 该字段不展示
    inlines = [LessionInline]                              # 同一个model注册两个管理器
    list_editable = ['degree','desc']                    # 可以在列表直接修改
    style_fields = {'detail': 'ueditor'}  # 看xadmin/plugins/ueditor
    import_excel = True  # 看xadmin/plugins/excel

    def queryset(self):
        qs = super(BannerCourseAdmin,self).queryset()
        qs = qs.filter(is_banner=True)
        return qs

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            pass
        return super(BannerCourseAdmin, self).post(request, args, kwargs)


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course', 'name', 'download', 'add_time']


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)