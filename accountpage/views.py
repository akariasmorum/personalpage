from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import traceback
from .forms import Message
from datetime import datetime
import http.client as hc
import json
import logging
from .auth_esia import Auth_esia
from .forms import SignUpForm, CallDocForm, Patient, AddChildForm, MessageForm, LoginForm, CallDoctorForm
from .models import PatientUser
import base64

def redirect_esia(request):
	auth = Auth_esia()
	url = auth.generate_uri()

	return redirect(url)

def esia_callback(request):
	if 'code' in request.GET:
		auth = Auth_esia()

		#генерация параметров для запроса маркера доступа
		auth.generate_access_token_params(request.GET.get('code'))

		#запрос маркера доступа
		r = auth.post_access_token_params()


		mas = json.loads(r.text)
		#print('mas: {0}'.format(mas['access_token']))
		access_token = mas['access_token']

		#access_token - строка, состоящая из 3ех параметров, разделенных точкой
		#header.data.signature, закодированных в формате base64
		spl = mas['access_token'].split('.')

		encoded_data = spl[1]

		#base64 кодируется 4мя символами и бывает, что в конце блока не достает
		#знаков =, поэтому дополняем строку знаками =, пока длина строки не
		#будет равна 4
		encoded_data += '=' * (-len(encoded_data) % 4)


		decoded = base64.urlsafe_b64decode(encoded_data)
		decoded_json = json.loads(decoded)
		oid = str(decoded_json['urn:esia:sbj_id'])

		#запрос снилса пациента по указанному OID
		snils = auth.request_user_snils(access_token, oid)
		print ('snils {0}'.format(snils))

		#Получаем пациента по возвращенному с ЕСИА СНИЛСу
		patient = PatientUser.objects.get(snils = snils)


		if patient is None:
			return HttpResponce('<h2>Пользователь с таким СНИЛС не зарегистрирован в системе</h2>')
		else:
			login(request, patient)
			return redirect('/main')

	elif 'access_token' in request.GET:

		return HttpResponse('<h2>Hello TOKEN: {0}</h2>'.format(request.GET.get('access_token')))



logger = logging.getLogger('django')
#
#ЛОГИН
#



def loginView(request):
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
								'pacients': request.session['pacients']
								  })

######################




#просмотр детей
@login_required(login_url='/login')
class ChildrenView(generic.ListView):
	model = Patient
	context_object_name = 'children'
	template_name = 'mypage.html'

	'''def get_queryset(self):
		return Patient.objects.filter(trustee = self.request.user)
'''
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['children'] = Patient.objects.filter(trustee = self.request.user)
		return context


	'''def __init__(self, user, *args, **kwargs):
		super(ChildrenView, self).__init__(*args, **kwargs)
		self.queryset = Patient.objects.filter(trustee = user)'''


#######################




#моя страница #####################
@login_required(login_url='/login')
def mypage(request):
	return render(request, 'mypage.html',
		context= {'title': 'Моя информация', 'nbar': 'mypage',
				   'name': (request.user.surname + ' ' + request.user.name),
			   #'children': children, 'form': form,
			    'pacients': request.session['pacients'],
			  })

	'''
	children = Patient.objects.filter(trustee = request.user)
	if request.method =='POST':
		form = AddChildForm(request.POST)
		if form.is_valid():
			form.save(request.user)
	else:
		form = AddChildForm()
	return render(request, 'mypage.html',
		context= {'title': 'Моя информация', 'nbar': 'mypage',
				   'name': (request.user.surname + ' ' + request.user.name),
			   'children': children, 'form': form,
			   'pacients': request.session['pacients']})
 '''

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



#вызов врача на дом
@login_required(login_url='/login')
def calldoc(request):
	if request.method =='POST':
		if request.POST["status_send"] == "false":
			form = CallDoctorForm(request.POST)
			if form.is_valid():
				form.save_data(request.user.snils, request.POST)


	form = CallDoctorForm()
	pacients = request_user_adress(request.user.snils)

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
		           'drug_records': get_ehr_PrescriptionDrugs(request),
		           'pacients':request.session['pacients']
		         })
###---end|ЭМК---####


####---Получить назначенные лекарственные препараты---####
def get_ehr_PrescriptionDrugs(request):
	#request.method = 'POST'
	return BadBusExchangeMethod(
		request,
		'EHMK.PrescriptionDrugs',
		{
		#"snils":request.POST.get('snils')
		"snils":request.user.snils,
	     #"snils":"074-500-645 44"
	    },
	    ['output','EHMK.PrescriptionDrugs'])
###---end|Получить назначенные лекарственные препараты---####

####---Получить назначенные лекарственные препараты---####
def get_ehr_ListDocuments(request):
	#request.method = 'POST'
	return BadBusExchangeMethod(
		request,
		'EHMK.ListDocuments',
		{
			#"snils":       request.POST.get('snils')
			#"snils":"032-524-797 39",
			"snils":request.user.snils,
		},
		['output','EHMK.ListDocuments'])
###---end|Получить назначенные лекарственные препараты---####



#Запись на прием
@login_required(login_url='/login')
def app(request):
	return render(request, 'appointment.html',
	context={'title': 'Запись на прием',
	'nbar': 'app', 'name': (request.user.surname + ' ' + request.user.name) })

@login_required(login_url='/login')
def therapist(request):
	return render(request, 'schedule_therapist.html',
	              context={'title': 'Расписание участкового врача',
	                        'nbar': 'therapist',
	                    'pacients': request.session['pacients']})

@login_required(login_url='/login')
def main(request):
	return render(request, 'main.html',
	              context={'title': 'Главная',
	                        'nbar': 'main',
	                    })

#####################
def get_docs_list(request):
	''' Список документов по снилсу '''
	return busExchangeMethod(
		request,
		'EHMK.ListDocuments',
		{
			"snils":request.POST.get('snils'),
		},
		['output','EHMK.ListDocuments'])

def get_drugs_list(request):
	''' Назначение лек.препара по снилсу '''
	return busExchangeMethod(
		request,
		'EHMK.PrescriptionDrugs',
		{
			"snils":request.POST.get('snils'),
		},
		['output','EHMK.PrescriptionDrugs'])

def send_call_doctor(request):
	'''
	послать вызов врача на дом в ИШ
	'''

	return busExchangeMethod(
		request,
		'CallDoctorNew',
		{
							"snils":       request.POST.get('snils'),
							"id_doc_site": request.POST.get('id_doc_site'),
							"datedoc":     datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
							"temperature": request.POST.get('temperature'),
							"complaint":   request.POST.get('complaint'),
							"kladr": 	   request.POST.get('kladr'),
							"house":       request.POST.get('house'),
							"room":        request.POST.get('room'),
							"phone":       request.POST.get('phone'),
							"email":       request.user.email,
							"addit_inform":request.POST.get('addit_inform'),
		},
		['message'])


def get_dictrict_doctor_info(request):
	pass


#Информация об участковом терапевте
def get_district_doctor_info(request):

	return busExchangeMethod(
		request,
		'DistrictDoctor',
		{
			"snils":       request.POST.get('snils'),
		},
		['output','DistrictDoctor'])




#Раписание приёма участкового терапевта
def get_dictrict_doctor_schedule(request):

	snils = request.POST.get('snils')
	date = request.POST.get('date')


	sched =  busExchangeMethod(
		request,
		'ScheduleDistrictDoctor',
		{
			"snils":       snils,
			"date" :       date
		},
		['output','ScheduleDistrictDoctor'])

	return sched



def get_doc_day_schedule(request):
	pass


def get_schedule_month(request):
	'''
	запрос расписания на указанный месяц для указанного пациента
	'''

	print (request.POST)
	return busExchangeMethod(
		request,
		'CalendarList',
		{
			"snils": request.POST.get('snils'),
			"date_begin": request.POST.get('date_begin'),
			"date_end": request.POST.get('date_end'),
			"amount": request.POST.get('amount'),
		},
		['output', 'CalendarList'])


def busExchangeMethod(request, method, params_dict, nestedKeys):
	'''
	Общий метод для работы с IBUS:
	Arguments:
		request - стандартный request для всех методов view
		method  - string, название метода, который вызываем у IBUS
		params_dict - dict, параметры метода
		returnableParam - string, название возвращаемого узла

	Output:
		HttpResponce строка либо с данными, либо с сообщением ошибки, либо с сообщением, что
		get- методам  тут делать нечего
	'''

	if request.method == 'POST':
		try:
			responce = IbusScriptExcecutor(*DEVELOPING_INIT_ARGUMENTS).post_message(method, params_dict)
			print(responce)
		except Exception as Ex:
			print(traceback.format_exc())
			responce = str(Ex)
		if 'ErrorsType:' in responce['output']:
			return HttpResponse(responce['output']['ErrorsType:'])


		if len(nestedKeys) == 1:
			#print(responce)
			print(responce[nestedKeys[0]])
			return HttpResponse(responce[nestedKeys[0]])
		elif len(nestedKeys) == 2:
			print(responce[nestedKeys[0]][nestedKeys[1]])
			print(type(responce[nestedKeys[0]][nestedKeys[1]]))
			return HttpResponse(responce[nestedKeys[0]][nestedKeys[1]])

	else:
		return HttpResponse('Nothing to do here!')

def BadBusExchangeMethod(request, method, params_dict, nestedKeys):

		try:
			responce = IbusScriptExcecutor(*DEVELOPING_INIT_ARGUMENTS).post_message(method, params_dict)
			#print(responce)
		except Exception as Ex:
			#print(traceback.format_exc())
			responce = str(Ex)

		if len(nestedKeys) == 1:
			return json.loads(responce[nestedKeys[0]])
		elif len(nestedKeys) == 2:
			#print (nestedKeys[0],nestedKeys[1])
			#print ('info :',responce)
			return json.loads(responce[nestedKeys[0]][nestedKeys[1]])




#проверяет,
#возвращает true, если у текущего пользователя есть опекаемый с таким снилс у и этого опекаемого есть указанный адрес
def safe_calldoc_check(request, snils, kladr, house, room):

	'''
	Проверить, есть ли у этого пользователя такой опекаемый, и есть ли у опекаемого такой адрес

	Args:
		request ....,
		snils   - string, снилс указанного пациента,
		kladr   - string, кладр указанного адреса,
		house   - string, номер дома указанного адреса,
		room    - string, номер квартиры указанного адреса

	Output:
		true - если у данного пользователя есть такой опекаемый, и у этого опекаемого есть такой адрес
		false в иных случаях.(когда какая сволочь post не через форму пытается просунуть)
	'''

	children = request_user_adress(request.user.snils)
	for child in children:
		if child['SNILS'] == snils:
			for adress in child['adresses']:
				if (adress['KLADR'] == kladr and
					adress['dom'] == house and
					adress['kvstr'] == room):
					return true
	return false

def safe_schedule_check(request, snils):
	'''
	Проверить, есть ли данного юзера такой пациент. чтобы нельзя было чужим людям узнавать расписание

	Arguments:
		request - ...
		snils - string, снилс выбранного пациента
	'''
	pass


def send_message(request):
	if request.method =='POST':
		message_form = MessageForm(request.POST)

		if message_form.is_valid():
			print('сработало!')
			message = message_form.save(commit=False)
			message.sender = request.user
			message.save()
			print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
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
			return resp
		else:
			print(str(message_form.errors))
			return HttpResponse(str(message_form.errors))


			'''
			responce = None
			try:
				responce = IbusScriptExcecutor(*DEVELOPING_INIT_ARGUMENTS).post_message('MessagePacientNew',
					)
				print(responce)

			except Exception as Ex:
				print(str(traceback.format_exc()))
				responce = str(Ex)

			return HttpResponse(str(responce['message']))



		else:
			print(message_form.errors)


	else:
		return HttpResponse('Нет данных для отправки!')'''



####Календарь пациента
def calendar(request):
	con = hc.HTTPConnection('ibus.dgkb.lan', 80)
	headers = {
	'Authorization': 'Basic cm9vdDpyb290',
	'Host': 'localhost:5000',
	'Content-Type': 'application/json'
	}

	parametr = str(json.dumps({'snils': '123123123'}))



	body = json.dumps({
	'name': 'CalendarList',
	'params': {'request': parametr}
	})

	con.request('POST', '/api/executescript', body=body, headers=headers)

	c = con.getresponse().read().decode()
	a = json.loads(c)

	x= json.loads(a['output']['CalendarList'])

	data = []
	for dates in x:
		first = [dates['NRU_GROUP'], dates['datedoc']]
		data.append(first)


	return render(request, 'calendar.html', context = {'title': 'Календарь пациента', 'nbar': 'calendar', 'data':  data})

#####



#выход из системы
def user_logout(request):
	logout(request)
	return redirect('login')

#запросить опекаемых данным польователем
#output: list [] опекаемых
def request_user_children(snils):
	try:
		children = IbusScriptExcecutor(*DEVELOPING_INIT_ARGUMENTS).post_message(
			'PacientList',
			{'snils':snils})
		pacient_list_json = json.loads(children['output']['PacientList'])

		return pacient_list_json
	except Exception as Ex:
		return []

#запросить адреса данного пациента
#output: list[ { адрес }, { адрес } ]
def request_adress(snils):
	#print ('snils ',snils)
	adress = IbusScriptExcecutor(*DEVELOPING_INIT_ARGUMENTS).post_message('AddressList',
		 {'snils': snils})
	#print (adress['output'])
	adress_list_json = json.loads(adress['output']['AddressList'])

	return adress_list_json


#запрашивает опекаемых и их адреса, и упаковывает эту информацию в dict
#output: list [{пациент, адреса пациента:[]}, {пациент, адреса пациента:[]}]
def request_user_adress(snils):

	pacients = request_user_children(snils)
	# error  вот тут ошибка СНИЛС ПУСТОЙ!

	for pacient in pacients:
		#print(pacient['SNILS'])
		adresses = request_adress(pacient['SNILS'])
		pacient['adresses'] = adresses
	#print(pacients)
	return pacients

class SignUp(generic.CreateView):
	form_class = SignUpForm
	success_url = reverse_lazy('login')
	template_name = 'signup.html'


##если есть intance, То вернет существующее, если нет, то создаст новое
class Singleton:
	__instance = None
	def __new__(cls, *args, **kwargs):
		if not cls.__instance:
			cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
		return cls.__instance


#параметры для IbusScriptExecutor.__init__() на время разработки
DEVELOPING_INIT_ARGUMENTS = ['localhost', '5000', 'ibus.dgkb.lan', '80']
## всегда одно соединение с ИШ
class IbusScriptExcecutor():

	def __init__(self, host, host_port, bus_adress, bus_port):
		try:
			self.con = hc.HTTPConnection(bus_adress, bus_port)
			self.headers = {
			'Authorization': 'Basic cm9vdDpyb290',
			'Host': host+':'+ host_port,
			'Content-Type': 'application/json'
			}
		except Exception as connectionEx:
			raise Exception('Не удалось подключиться к серверу! Попробуйте позже')


	#Отправить сообщение в Шину
	#input:
	#method - str / какой использует метод API
	#body_dic - dic / словарь параметров body
	#output: js  - str / ответ сервера в формате json
	def post_message(self, method,   body_dic):
		parameter = str(json.dumps(body_dic))

		body = json.dumps({
		'name': method,
		'params': {'request': parameter}
		})
		#print (body)
		#rint (method)

		self.con.request('POST', '/api/executescript', body=body, headers=self.headers)
		resp = self.con.getresponse().read()
		decoded_response = resp.decode()
		#print(resp)
		js = json.loads(decoded_response)

		return js
