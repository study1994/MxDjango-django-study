# _*_ coding:utf-8 _*_
from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger    # 用于分页
from django.http import HttpResponse                                  # 指定返回给用户的类型
from django.db.models import Q                                        # Q表示或

from .models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin                      # 引进一个基础的View

# Create your views here.


# 课程列表首页
class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by('-add_time')
        hot_courses = Course.objects.all().order_by('-click_nums')[:3]

        # 课程搜索 (全局导航栏中)
        search_keywords = request.GET.get('keywords','')
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords)|Q(detail__icontains=search_keywords))      # name__icontains表示包含

        #课程排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_courses = all_courses.order_by('-students')
            elif sort == 'hot':
                all_courses = all_courses.order_by('-click_nums')

        #对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 5, request=request)
        courses = p.page(page)

        return render(request, 'course-list.html', {
            'all_courses':courses,
            'sort':sort,
            'hot_courses': hot_courses
        })


# 课程详情页
class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        # 增加课程点击数
        course.click_nums += 1
        course.save()

        # 课程/机构收藏
        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated():
            #判断用户是否登陆
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True

            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # 找到相关课程
        tag = course.tag
        if tag:
            relate_coures = Course.objects.filter(tag=tag)[:2]
        else:
            relate_coures = []

        return render(request, 'course-detail.html', {
            'course':course,
            'relate_coures':relate_coures,
            'has_fav_course':has_fav_course,
            'has_fav_org':has_fav_org
        })


# 课程章节信息
class CourseInfoView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.students += 1
        course.save()

        # 查询用户是否已经学习了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            """
           这里不用user_courses.user = request.user;user_courses.course = course
           因为 user，course 是外键，在 UserCourse 实际上存储的是 id ，这些 id 是已经存在的
           """
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 得出学过该课程的同学还学过的课程
        user_courses =UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        # 这句话的意思是只要user_ids在这个列表中，就会返回回来。
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        #现在取出所有课程id
        course_ids = [user_course.course.id for user_course in user_courses]
        #获取学过该用户学过其他的所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-video.html', {
            'course':course,
            'course_resources':all_resources,
            'relate_courses':relate_courses
        })


# 课程评论
class CommentsView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        #课程评论页面与章节页面重复的地方
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course)

        return render(request, 'course-comment.html', {
            'course':course,
            'course_resources':all_resources,
            'all_comments': all_comments
        })

    def post(self, request, course_id):
        # 得出学过该课程的同学还学过的课程
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all()

        return render(request, 'course-comment.html', {
            'course':course,
            'course_resources':all_resources,
            'all_comments':all_comments
        })


# 添加评论
class AddCommentsView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            # 判断用户登录状态
            return HttpResponse('{"status":"fail", "msg": "用户未登录"}', content_type='application/json')

        course_id = request.POST.get('course_id', 0)
        comments = request.POST.get('comments', '')
        if course_id > 0 and comments:
            course_comments = CourseComments()
            course = Course.objects.get(id = (course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg": "添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg": "添加失败"}', content_type='application/json')


# 视频播放页面/课程信息
class VideoPlayView(View):
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course
        course.students += 1
        course.save()

        # 查询用户是否关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)

        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        # # 这句话的意思是只要user_ids在这个列表中，就会返回回来。
        # all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 现在取出所有课程id
        course_ids = [user_course.course.id for user_course in user_courses]
        # 获取学过该用户学过其他的所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-play.html', {
            'course': course,
            'course_resources': all_resources,
            'relate_courses': relate_courses,
            'video': video
        })