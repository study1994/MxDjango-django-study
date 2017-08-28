# _*_ coding:utf-8 _*_
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger #用于分页
from django.http import HttpResponse #指定返回给用户的类型
from django.db.models import Q #Q表示或

from .models import CourseOrg, CityDict, Teacher

from operation.models import UserFavorite

from course.models import Course
from .forms import UserAskForm
from course.models import Course
# Create your views here.


# 课程机构列表页，筛选页【课程机构列表功能】
class OrgView(View):
    def get(self,request):
        #课程机构
        all_orgs = CourseOrg.objects.all()
        hot_orgs = all_orgs.order_by('-click_nums')[:3]
        #城市
        all_citys = CityDict.objects.all()
        # 机构搜索 (全局导航栏中)-----------------------------------------------------------------------------
        search_keywords = request.GET.get('keywords', '')         # 根据机构级别和所在地区得到列表
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))       # 机构描述或机构名称包含这个关键词
        # -----------------------------------------------------------------------------------------------------
        #取出筛选城市【所在地区筛选】
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))
        #类别筛选 【所机构类别筛选】
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)
        # 排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by('-students')
            elif sort == 'courses':
                all_orgs = all_orgs.order_by('-course_nums')
        # 筛选完成之后再进行统计
        org_nums =all_orgs.count()

        # 对课程机构进行分页-------------------------------------------------------------
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_orgs, 5, request=request)
        orgs = p.page(page)

        return render(request, 'org-list.html', {
                'all_orgs':orgs,            # 所有机构【进过分页后】
                'all_citys':all_citys,      # 所在地区
                'org_nums':org_nums,        # 共多少家
                'city_id':city_id,
                'category':category,
                'hot_orgs':hot_orgs,        # 授课机构排名
                'sort': sort
        })


# 用户添加咨询课程表单提交
class AddUserAskView(View):
    def post(self, requset):
        userask_form = UserAskForm(requset.POST)          # 实例化
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)     # 直接将数据库保存
            # json字符串{"status":"success"}，浏览器会将其解析成json，而后面那个是固定不变的
            return HttpResponse('{"status":"success"}', content_type='application/json')    # 异步提交【直接在这个页面返回】
        else:
            # return HttpResponse("{'status':'fail','msg':{0})".format(userask_form.errors),content_type='application/json')
            return HttpResponse('{"status":"fail", "msg": "添加出错"}', content_type='application/json')    # 对应org-list.html的<script></sctipt>语句


# 课程机构详情页的首页
class OrgHomeView(View):
    def get(self, request,org_id):
        current_page = 'home'
        course_org = CourseOrg.objects.get(id = int(org_id))
        course_org.click_nums += 1                     # 增加课程机构点击量+1
        course_org.save()
        has_fav = False                                 # 判断用户是否收藏
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()[:3]           # course_set反向取出所有课程【注意写】
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html',{
            'all_courses':all_courses,
            'all_teachers':all_teachers,
            'course_org':course_org,
            'current_page':current_page,
            'has_fav':has_fav
        })


# 课程机构首页【全部课程】
class OrgCourseView(View):
    def get(self, request,org_id):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id = int(org_id))
        has_fav = False           # 判断用户是否收藏
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()            # course_set反向取出所有课程
        return render(request, 'org-detail-course.html',{
            'all_courses':all_courses,
            'course_org':course_org,
            'current_page': current_page,
            'has_fav':has_fav
        })


# 课程机构介绍页
class OrgDescView(View):
    def get(self, request,org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id = int(org_id))
        has_fav = False      # 判断用户是否收藏
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html',{
            'course_org':course_org,
            'current_page': current_page,
            'has_fav':has_fav
        })


# 课程机构详情页讲师页面
class OrgTeacherView(View):
    def get(self, request,org_id):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id = int(org_id))

        has_fav = False              # 判断用户是否收藏
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        all_teachers = course_org.teacher_set.all()#course_set反向取出所有课程
        return render(request, 'org-detail-teachers.html',{
            'all_teachers':all_teachers,
            'course_org':course_org,
            'current_page': current_page,
            'has_fav':has_fav
        })


# 用户收藏,以及用户取消收藏
class AddFavView(View):
    def post(self,request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)        # 收藏的类型
        if not request.user.is_authenticated():
            return HttpResponse('{"status":"fail", "msg": "用户未登录"}', content_type='application/json')
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_records:       # 记录已经存在， 则表示用户取消收藏
            exist_records.delete()

            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()

            if int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()

            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return HttpResponse('{"status":"success", "msg": "收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()

                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                if int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()

                return HttpResponse('{"status":"success", "msg": "已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg": "收藏出错"}', content_type='application/json')

# 讲师列表页
class TeacherListView(View):
    def get(self, request):
        all_teachers = Teacher.objects.all()
        # 课程讲师搜索 (全局导航栏中)
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(
                Q(name__icontains=search_keywords) |
                Q(work_company__icontains=search_keywords) |
                Q(work_position__icontains=search_keywords))


        #排序功能展示（根据人气排行）
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'hot':
                all_teachers = all_teachers.order_by('-click_nums')

        #讲师排行榜
        sorted_teacher = Teacher.objects.all().order_by('-click_nums')[:3]

        # 对讲师进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_teachers, 3, request=request)

        teachers = p.page(page)

        return render(request, 'teachers-list.html', {
            'all_teachers':teachers,
            'sorted_teacher':sorted_teacher,
            'sort':sort
        })


# 讲师详情页
class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id = int(teacher_id))
        teacher.click_nums +=1
        teacher.save()
        all_courses = Course.objects.filter(teacher=teacher)

        has_teacher_faved = False
        # 注意这里有个坑就是 teacher_id 是字符串，teacher.id 是数字
        if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
            has_teacher_faved = True

        has_org_faved = False
        if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
            has_org_faved = True

        #讲师排行榜
        sorted_teacher = Teacher.objects.all().order_by('-click_nums')[:3]
        return render(request, 'teacher-detail.html', {
            'teacher':teacher,
            'all_courses':all_courses,
            'sorted_teacher':sorted_teacher,
            'has_teacher_faved':has_teacher_faved,
            'has_org_faved':has_org_faved
        })