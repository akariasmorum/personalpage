from django.conf.urls import url, include
#import django.contrib.auth.urls

from . import views
from . import forms

urlpatterns = [
	url(r'^$', views.loginView, name='login'),
	url(r'^login', views.loginView, name='login'),
	url(r'^main', views.main, name='main'),
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
	url(r'^therapist-schedule', views.therapist, name='therapist'),
	url(r'^get-doc-schedule-day', views.get_doc_day_schedule, name='doc-day-shedule'),
	url(r'^get-district-doctor-info', views.get_district_doctor_info, name='district_doctor'),
	url(r'^get-schedule-district-doctor', views.get_schedule_district_doctor, name='schedule_district_doctor'),

	#EHR links
	url(r'^get-docs-list', views.get_docs_list, name='get-docs-list'),
	url(r'^get-drugs-list', views.get_drugs_list, name='get-drugs-list'),
]
