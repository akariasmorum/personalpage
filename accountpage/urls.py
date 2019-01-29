from django.conf.urls import url, include
#import django.contrib.auth.urls

from . import views
from . import forms
from . import views_ibus_connector
from . import test_bus_connector

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
	#url(r'^calendar', views.calendar, name='calendar'),
	url(r'^message', views.get_message, name='message'),
	url(r'^mypage', views.mypage, name = 'my-page'),
	url(r'^send-message', views.send_message, name='send-message'),
	url(r'^send-calldoc', views_ibus_connector.send_call_doctor, name ='send-calldoc'),
	url(r'^get-month-schedule', views_ibus_connector.get_schedule_month, name = 'get-month-schedule'),
	url(r'^therapist-schedule', views.therapist, name='therapist'),
	#url(r'^get-doc-schedule-day', views_ibus_connector.get_doc_day_schedule, name='doc-day-shedule'),

	url(r'^get-district-doctor-info', views_ibus_connector.get_district_doctor_info, name='district_doctor'),
	url(r'^get-schedule-district-doctor', views_ibus_connector.get_dictrict_doctor_schedule, name='schedule_district_doctor'),

	#EHR links
	url(r'^get-docs-list', views_ibus_connector.get_docs_list, name='get-docs-list'),
	url(r'^get-drugs-list', views_ibus_connector.get_drugs_list, name='get-drugs-list'),

	url(r'^get-dictrict-doctor-schedule', views_ibus_connector.get_dictrict_doctor_schedule, name='dictrict_doctor_schedule'),
	url(r'^get-district-doctor-info', views_ibus_connector.get_district_doctor_info, name='district_doctor_info'),
	
	url(r'^redirect-esia', views.redirect_esia, name = 'redirect-esia'),
	url(r'^esia_callback', views.esia_callback, name = 'callback'),

	url(r'^xyz', test_bus_connector.sched1, name = 'test-bus'),
	url(r'^qwerty', views.schedule_test, name='test-schedule'),
]
