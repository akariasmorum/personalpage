from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import traceback

from datetime import datetime
import json
import logging
from .auth_esia import Auth_esia
from .forms import SignUpForm, CallDocForm, Patient, AddChildForm, MessageForm, LoginForm, CallDoctorForm

import base64
from .views_ibus_connector import (get_ehr_PrescriptionDrugs, get_ehr_ListDocuments, get_docs_list,
	get_drugs_list,	send_call_doctor, get_district_doctor_info, get_dictrict_doctor_schedule, get_schedule_month,
	busExchangeMethod, BadBusExchangeMethod, request_user_children, request_adress, request_user_adress, get_check_code	)
from .auth_esia import redirect_esia, esia_callback
import time

logger = logging.getLogger('django')


class SignUp(generic.CreateView):
	'''
	Регистрация в системе
	'''
	form_class = SignUpForm
	success_url = reverse_lazy('login')
	template_name = 'signup.html'


def loginView(request):
	'''
	Вход в систему
	'''
	if request.method == 'POST':
		form = LoginForm(request.POST)

		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			login_user = authenticate(username = username, password = password)
			if login_user:
				login(request, login_user)
				#print ('инфо',str(request.session))
				return redirect('/main')

	else:
		form = LoginForm()

	return render(request, 'login.html', context = {'title':'Аутентификация', 'form': form})

#########################



###Расписание#########
@login_required(login_url='/login')
def schedule(request):
	return render(request, 'schedule.html',
	                      context={'title': 'Расписание',
						            'nbar': 'schedule',
									'name': (request.user.surname + ' ' + request.user.name),
									'pacients': request.session['pacients'],
									'method_url': 'get-month-schedule'
								  })

######################

@login_required(login_url='/login')
def schedule_test(request):
	
	return render(request, 'schedule.html',
	                      context={'title': 'Расписание',
						            'nbar': 'schedule',
									'name': (request.user.surname + ' ' + request.user.name),
									'pacients': request.session['pacients'],
									'method_url': "xyz"
								  })





#моя страница #####################
@login_required(login_url='/login')
def mypage(request):
	return render(request, 'mypage.html',
		context= {'title': 'Моя информация', 'nbar': 'mypage',
				   'name': (request.user.surname + ' ' + request.user.name),
			   #'children': children, 'form': form,
			    'pacients': request.session['pacients'],
			  })

############################



#Обращение пациента
@login_required(login_url='/login')
def get_message(request):

	form = MessageForm()
	return render(request, 'message.html',
			   context={'title': 'Расписание', 'nbar': 'message',
						 'form': form,
						 'name': (request.user.surname + ' ' + request.user.name),
					 'my_email': 'email@email.ru',
					 'my_phone': '+7(987)123-32-23',
					   'hidden': ['status_send','date','id_doc_site'],
					 'pacients': request.session['pacients']
					 })

################################


def send_message(request):
	start_time = time.time()
	'''
	Обращение пациента
	'''
	if request.method =='POST':
		message_form = MessageForm(request.POST)

		if message_form.is_valid():
			
			message = message_form.save(commit=False)
			message.sender = request.user
			message.save()
			
			resp =  busExchangeMethod(
					request,
					'MessagePacientNew',
					{
							"snils": request.POST.get('snils'),
							"id_doc_site": request.POST.get('id_doc_site'),
							"datedoc": 	datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
							"recipient": request.POST.get('recipient'),
							"subject": request.POST.get('subject'),
							"message": request.POST.get('message'),
							"phone":   request.POST.get('phone'),
							"email":   request.user.email
					},
					['message'])
			print(resp)
			print("--- %s seconds ---" % (time.time() - start_time))
			return resp
		else:
			print(str(message_form.errors))
			return HttpResponse(str(message_form.errors))


#вызов врача на дом
@login_required(login_url='/login')
def calldoc(request):
	if request.method =='POST':
		if request.POST["status_send"] == "false":
			form = CallDoctorForm(request.POST)
			if form.is_valid():
				form.save_data(request.user.snils, request.POST)


	form = CallDoctorForm()
	pacients = request_user_adress(request, request.user.snils)

	return render(request, 'calldoc.html',
		 context={'title': 'Вызов врача на дом', 'nbar': 'call-doc',
				   'form': form,
				   'name': (request.user.surname + ' ' + request.user.name),
			   'my_email': 'email@email.ru',
			   'my_phone': '+7(987)123-32-23',
				 'hidden': ['status_send', 'date',
							'id_doc_site', 'kladr' ,
								 'house' , 'room'],
				'pacients': pacients
				 })
###############################


####---ЭМК---####
@login_required(login_url='/login')
def ehr(request):

	return render(request, 'ehr.html',
		 context={'title': 'Электронная медицинская карта', 'nbar': 'ehr',
		           'name': (request.user.surname + ' ' + request.user.name),
		           'docs': [],#get_ehr_ListDocuments(request) ,
		           'drug_records': [],
		           'pacients':request.session['pacients']
		         })
###---end|ЭМК---####



@login_required(login_url='/login')
def app(request):
	'''
	Запись на прием
	'''
	return render(request, 'appointment.html',
	context={'title': 'Запись на прием',
	'nbar': 'app', 'name': (request.user.surname + ' ' + request.user.name) })

###################################

@login_required(login_url='/login')
def therapist(request):
	'''
	Расписание участкового врача
	'''
	return render(request, 'schedule_therapist.html',
	              context={'title': 'Расписание участкового врача',
	                        'nbar': 'therapist',
	                    'pacients': request.session['pacients']})
###################################

@login_required(login_url='/login')
def main(request):
	'''
	Моя информация
	'''
	return render(request, 'main.html',
	              context={'title': 'Главная',
	                        'nbar': 'main',
	                    })

###################################	



def user_logout(request):
	'''
	Выход из системы
	'''
	logout(request)
	return redirect('login')

###################################	


		


