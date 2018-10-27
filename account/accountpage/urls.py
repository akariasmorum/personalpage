from django.conf.urls import url, include
import django.contrib.auth.urls

from . import views
from . import forms

urlpatterns = [
	url(r'', include(django.contrib.auth.urls)),
	url('call', views.calldoc, name='call-doc'),
	url('ehr', views.ehr, name='ehr'),
	url('appointment', views.app, name='appointment'),
	url('schedule', views.schedule, name='schedule'),
	url('calendar', views.calendar, name='calendar'),
	url('message', views.get_message, name='message'),
	url('signup', views.SignUp.as_view(), name = 'signup'),
]