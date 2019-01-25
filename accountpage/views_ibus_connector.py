from django.http import HttpResponseRedirect, HttpResponse
import http.client as hc
import json
import traceback
from .models import PatientUser
from datetime import datetime
import base64


'''
	Здесь содержатся все методы, нужные для общения с Интеграционной Шиной
'''


class Singleton:
	__instance = None

	def __new__(cls, *args, **kwargs):
		if not cls.__instance:
			cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
		return cls.__instance


DEVELOPING_INIT_ARGUMENTS = ['localhost', '5000', 'ibus.dgkb.lan', '80']


class IbusScriptExcecutor():

	def __init__(self, host, host_port, bus_adress, bus_port):
		try:
			self.con = hc.HTTPConnection(bus_adress, bus_port)
			self.headers = {
			'Authorization': 'Basic cm9vdDpyb290',
			'Host': host + ':' + host_port,
			'Content-Type': 'application/json'
			}
		except Exception as connectionEx:
			raise Exception('Не удалось подключиться к серверу! Попробуйте позже')
	
	def post_message(self, method,   body_dic):
		'''
		Отправить сообщение в Шину
		input:
			method - str / какой использует метод API
			body_dic - dic / словарь параметров body
		output: 
			js  - str / ответ сервера в формате json
		'''	

		parameter = str(json.dumps(body_dic))

		body = json.dumps({
		'name': method,
		'params': {'request': parameter}
		})		

		self.con.request(
			'POST',
			'/api/executescript', 
			body=body,
			headers=self.headers)		
			
		resp = self.con.getresponse()

		if resp.status != 200:
			raise Exception('Не удалось подключиться к шине!')
		else:	
			decoded_response = resp.read().decode()

			print('decoded_response: {0}'.format(decoded_response))
			js = json.loads(decoded_response)

			return js


def busExchangeMethod(request, method, params_dict, nestedKeys):
	'''
	Общий метод для работы с IBUS:
	Arguments:
		request - стандартный request для всех методов view
		method  - string, название метода, который вызываем у IBUS
		params_dict - dict, параметры метода
		nestedKeys - [], название возвращаемого узла. к примеру, 
			нормальный ответ от CalendarList 
			будет лежать в ['output']['CalendarList']


	Output:
		HttpResponce - строка либо с данными, 
			либо с сообщением['ErrorType:']ошибки,
			 либо с сообщением, что
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

		'''
		Бывает, что когда отсылаем данные,  нужно просто сообщение, 
		что скрипт выполнен, тогда его путь будет ['message']
		А когда запрашиваем данные, то они лежат в 
			['output']['*Название метода*']
		'''
		if len(nestedKeys) == 1:						
			return HttpResponse(responce[nestedKeys[0]])
		elif len(nestedKeys) == 2:			
			return HttpResponse(responce[nestedKeys[0]][nestedKeys[1]])

	else:
		return HttpResponse('Nothing to do here!')


def BadBusExchangeMethod(request, method, params_dict, nestedKeys):

		try:
			responce = IbusScriptExcecutor(*DEVELOPING_INIT_ARGUMENTS).post_message(method, params_dict)
			
		except Exception as Ex:
			
			responce = str(Ex)

		if len(nestedKeys) == 1:
			return json.loads(responce[nestedKeys[0]])
		elif len(nestedKeys) == 2:
			
			return json.loads(responce[nestedKeys[0]][nestedKeys[1]])


def get_ehr_PrescriptionDrugs(request):
	'''
	Получить назначенные лекарственные препараты
	'''
	
	return BadBusExchangeMethod(
		request,
		'EHMK.PrescriptionDrugs',
		{
		
		"snils":request.user.snils,
	    
	    },
	    ['output','EHMK.PrescriptionDrugs'])
###---end|Получить назначенные лекарственные препараты---####



def get_ehr_ListDocuments(request):
	'''
	Получить назначенные лекарственные препараты
	'''
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
							"phone":       request.POST.get('telephone'),
							"email":       request.user.email,
							"addit_inform":request.POST.get('addit_inform'),
		},
		['message'])


#Информация об участковом терапевте
def get_district_doctor_info(request):

	return busExchangeMethod(
		request,
		'DistrictDoctor',
		{
			"snils":       request.POST.get('snils'),
		},
		['output','DistrictDoctor'])


#Раcписание приёма участкового терапевта
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


def get_check_code(request, snils, code):
	'''
	Запрос с шины у юзера с таким пациентом такой регистрационный код
	arguments:
		snils 
		code - регистрационный код, который дают юзеру в ЛПУ, когда он даст согласие на обработку персональных данных
	output:
		Возвращает с сервера все позиции кодов для указанного регистрационного кода
		Если у такого пользователя дейcnвительно есть такой код,
		то длина возвращаемого массива будет больше 0
			return True
		Если нет регистрационного кода, 
			return False
	'''

	params_dict = {'snils': snils, 'code': code}
	method = 'RegistrationCheck'
	answer = BadBusExchangeMethod(request, method, params_dict, ['output', method])
	if len(answer) == 0:
		return False
	else:
		return True


def BadBusExchangeMethod(request, method, params_dict, nestedKeys):

		try:
			responce = IbusScriptExcecutor(*DEVELOPING_INIT_ARGUMENTS).post_message(method, params_dict)
			print(responce)
		except Exception as Ex:
			print(traceback.format_exc())
			responce = str(Ex)

		if len(nestedKeys) == 1:
			return json.loads(responce[nestedKeys[0]])
		elif len(nestedKeys) == 2:
			#print (nestedKeys[0],nestedKeys[1])
			#print ('info :',responce)
			return json.loads(responce[nestedKeys[0]][nestedKeys[1]])	


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


def request_user_children(snils):
	#запросить опекаемых данным польователем
	#output: list [] опекаемых	
	try:
		children = IbusScriptExcecutor(*DEVELOPING_INIT_ARGUMENTS).post_message(
			'PacientList',
			{'snils':snils})
		pacient_list_json = json.loads(children['output']['PacientList'])

		return pacient_list_json
	except Exception as Ex:
		return []


def request_adress(snils):
	#запросить адреса данного пациента
	#output: list[ { адрес }, { адрес } ]
	
	adress = IbusScriptExcecutor(*DEVELOPING_INIT_ARGUMENTS).post_message('AddressList',
		 {'snils': snils})
	
	adress_list_json = json.loads(adress['output']['AddressList'])

	return adress_list_json


def request_user_adress(snils):
	#запрашивает опекаемых и их адреса, и упаковывает эту информацию в dict
	#output: list [{пациент, адреса пациента:[]}, {пациент, адреса пациента:[]}]

	pacients = request_user_children(snils)
	
	for pacient in pacients:
		
		adresses = request_adress(pacient['SNILS'])
		pacient['adresses'] = adresses
	
	return pacients

