# -*- coding:utf-8 -*-

import  re
from django import forms

from operation.models import UserAsk  # model form


class UserAskForm(forms.ModelForm):
    class Meta:
        model = UserAsk                                   # 直接将model转换成form【前提是相似】
        fields = ['name', 'mobile', 'course_name']    # 挑选需要的form，也可以在上面新增字段

    def clean_mobile(self):    # 必须以clean开头
        """
        验证手机号码是否合法
        """
        mobile = self.cleaned_data['mobile']
        REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"      # 正则表达式基础
        p = re.compile(REGEX_MOBILE)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError(u'手机号码非法', code='mobile_invalid')    # code可以自定义
