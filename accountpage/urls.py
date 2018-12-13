from django.conf.urls import url, include
#import django.contrib.auth.urls

from . import views
from . import forms

urlpatterns = [
	url(r'^$', views.loginView, name='login'),
	url(r'^login', views.loginView, name='login'),
	url(r'^signup', views.SignUp.as_view(), name = 'signup'),
	url(r'^logout', views.user_logout, name = 'logout'),
	url(r'^call', views.calldoc, name='call-doc'),
	url(r'^ehr', views.ehr, name='ehr'),
	url(r'^appointment', views.app, name='appointment'),
	url(r'^schedule', views.schedule, name='schedule'),
	url(r'^calendar', views.calendar, name='calendar'),
	url(r'^message', views.get_message, name='message'),
	url(r'^mypage', views.mypage, name = 'my-page'),
	url(r'^send-message', views.send_message, name='send-message'),
	url(r'^send-calldoc', views.send_call_doctor, name ='send-calldoc'),
	url(r'^get-month-schedule', views.get_schedule_month, name = 'get-month-schedule'),
]