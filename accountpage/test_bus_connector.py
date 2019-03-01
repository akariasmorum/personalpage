from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import http.client as hc
import json
import time
import errno
from datetime import datetime

TEST_BUS_ADRESS = '10.130.4.219'
TEST_BUS_PORT = '8000'

DEFAULT_CHARSET = 'utf-8'
def test_bus_executor(parameters: dict, method: str):
	
	con = hc.HTTPConnection(TEST_BUS_ADRESS, TEST_BUS_PORT)

	headers = {
		'Authorization': 'Basic cm9vdDpyb290',
		'Host': 'localhost' + ':' + '8000',
		'Content-Type': 'application/json'
	}
	parameter = str(json.dumps(parameters))
	print(parameter)
	body = json.dumps({		
		'params': {'request': parameter}
		})
	try:
		con.request(
				'POST',
				'/API/'+method, 
				body=body,
				headers=headers)

	except Exception as ecr:
		print('test: ')
		print(ecr)
		if ecr.errno == errno.ECONNREFUSED:
			raise Exception('Извините, отсуствует соединение с базой данных, попробуйте позже')	
		else:
			raise Exception('Произошла ошибка при выполнении запроса: {0}'.format(ecr) )	
		
	resp = con.getresponse()
	data = json.loads(resp.read().decode('utf-8'))	
	print('data: ', data)
	if resp.status != 200:
		raise Exception('Сервер вернул код с ошибкой: {0}'.format(data))

	return data[method]



def sched1(request, snils, date_begin, date_end, amount):
	try:
		dic = {
			"snils": snils,
			"date_begin": date_begin,
			"date_end": date_end,
			"amount": amount,
		}
		data = test_bus_executor(dic, 'CalendarList')

		print('MODULE: sched1 | USER: {0} | TIME: {1} | PARAMS: {2}'.format(request,
														   datetime.now(),
														   dic ))

		return JsonResponse(data, safe=False)

	except Exception as e:
		print('MODULE: sched1 | USER: {0} | TIME: {1} | PARAMS: {2} | ERROR: {3}'.format(request,
																		datetime.now(),
																		dic,
																		str(e) ))
		return HttpResponse(str(e), status=500)
		
def is_user_accepted_permissions(request, snils):
	try:
		dic = {'snils': snils}
		a = test_bus_executor(dic, 
			'RegistrationCheck'
			)	

		print('MODULE: is_user_accepted_permissions | USER: {0} | TIME: {1} | PARAMS: {2}'.format(request,
														   datetime.now(),
														   dic ))	
		if len(a)>0:
			return True
		else:
			return False

	except Exception as e:
		print('MODULE: is_user_accepted_permissions | USER: {0} | TIME: {1} | PARAMS: {2} | ERROR: {3}'.format(request,
																		datetime.now(),
																		dic,
																		str(e) ))
		return HttpResponse(str(e), status=500)		

def get_drugs_list(request, snils):
	'''
	Получить назначенные лекарственные препараты
	'''
	try:
		dic = {"snils": snils}
		data = test_bus_executor(
			dic,
			'EHMK.PrescriptionDrugs'
			)

		print('MODULE: get_drugs_list | USER: {0} | TIME: {1} | PARAMS: {2}'.format(request,
														   datetime.now(),
														   dic ))			
		return JsonResponse(data, safe=False)

	except Exception as e:
		print('MODULE: get_drugs_list | USER: {0} | TIME: {1} | PARAMS: {2} | ERROR: {3}'.format(request,
																		datetime.now(),
																		dic,
																		str(e) ))
		return HttpResponse(str(e), status=500)	


def get_docs_list(request, snils):
	''' Список документов по снилсу '''
	try:
		dic = {"snils": snils}

		data = test_bus_executor(
			dic,
			'EHMK.ListDocuments'
			)

		print('MODULE: get_docs_list | USER: {0} | TIME: {1} | PARAMS: {2}'.format(request,
														   datetime.now(),
														   dic ))						
		return JsonResponse(data, safe=False)

	except Exception as e:
		print('MODULE: get_docs_list | USER: {0} | TIME: {1} | PARAMS: {2} | ERROR: {3}'.format(request,
																		datetime.now(),
																		dic,
																		str(e) ))
		return HttpResponse(str(e), status=500)	

def send_call_doctor(request, snils, id_doc_site, datedoc, temperature, complaint, kladr, house, room, phone, email, addit_inform):
	'''
	послать вызов врача на дом в ИШ
	'''
	try:
		dic = {
				"snils":       snils,
				"id_doc_site": id_doc_site,
				"datedoc":     datedoc,
				"temperature": temperature,
				"complaint":   complaint,
				"kladr": 	   kladr,
				"house":       house,
				"room":        room,
				"phone":       phone,
				"email":       email,
				"addit_inform":addit_inform,
			} 
		data = test_bus_executor(
			dic,	
			'CallDoctorNew'
		)				
		print('MODULE: send_call_doctor | USER: {0} | TIME: {1} | PARAMS: {2}'.format(request,
														   datetime.now(),
														   dic ))		
		return HttpResponse(data)

	except Exception as e:
		print('MODULE: send_call_doctor | USER: {0} | TIME: {1} | PARAMS: {2} | ERROR: {3}'.format(request,
																		datetime.now(),
																		dic,
																		str(e) ))
		return HttpResponse(str(e), status=500)		

def get_district_doctor_info(request, snils):

	try:
		dic = {
				"snils": snils, 
			}
		data = test_bus_executor(
			dic,	
			'DistrictDoctor'
		)				

		print('MODULE: get_district_doctor_info | USER: {0} | TIME: {1} | PARAMS: {2}'.format(request,
														   datetime.now(),
														   dic ))		

		return JsonResponse(data, safe=False)

	except Exception as e:
		print('MODULE: get_district_doctor_info | USER: {0} | TIME: {1} | PARAMS: {2} | ERROR: {3}'.format(request,
																		datetime.now(),
																		dic,
																		str(e) ))
		return HttpResponse(str(e), status=500)		

def get_dictrict_doctor_schedule(request, snils, date):

	try:
		dic = {
				"snils":       snils,
				"date":		   date,
			}
		data = test_bus_executor(
			dic,	
			'ScheduleDistrictDoctor'
		)			

		print('MODULE: get_disctrict_doctor | USER: {0} | TIME: {1} | PARAMS: {2}'.format(request,
														   datetime.now(),
														   dic ))		
		return JsonResponse(data, safe=False)

	except Exception as e:
		print('MODULE: get_disctrict_doctor | USER: {0} | TIME: {1} | PARAMS: {2} | ERROR: {3}'.format(request,
																		datetime.now(),
																		dic,
																		str(e) ))
		return HttpResponse(str(e), status=500)	

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

	try:
		dic = {
				'snils': snils,
				'search_code': code
			}

		data = test_bus_executor(
			dic,	
			'RegistrationCheck'
		)


		#TODO: заменить request на request.user.snils
		print('MODULE: get_check_code | USER: {0} | TIME: {1} | PARAMS: {2}'.format(request,
														   datetime.now(),
														   dic ))			
		return JsonResponse(data, safe=False)

	except Exception as e:
		print('MODULE: get_check_code | USER: {0} | TIME: {1} | PARAMS: {2} | ERROR: {3}'.format(request,
																		datetime.now(),
																		dic,
																		str(e) ))	
		return HttpResponse(str(e), status=500)	

def request_user_children(request, snils):

	#запросить опекаемых данным польователем
	#output: list [] опекаемых	
		

	if request.session.get('children') == None:
		print(2)
		try:
			print(3)
			dic = {
				"snils": snils, 
			}

			childrenList = test_bus_executor(
				dic,	
				'PacientList'
			)

			print('MODULE: request_user_children | USER: {0} | TIME: {1} | PARAMS: {2}'.format(request,
																		datetime.now(),
																		dic))

			request.session['children'] = childrenList
			
		except Exception as e:
			print('MODULE: request_user_children | USER: {0} | TIME: {1} | PARAMS: {2} | ERROR: {3}'.format(request,
																		datetime.now(),
																		dic,
																		str(e) ))
			

	return request.session['children']


def request_adress(request, snils):
	#запросить адреса данного пациента
	#output: list[ { адрес }, { адрес } ]

	try:
		data = test_bus_executor(
			{
				'snils': snils,			 	
			},	
			'AddressList'
		)

		#TODO: заменить request на request.user.snils
		print('MODULE: request_adress | USER: {0} | TIME: {1} | PARAMS: {2}'.format(request,
														   datetime.now(),
														   {'snils': snils} ))


		return JsonResponse(data, safe=False)

	except Exception as e:
		#TODO: заменить request на request.user.snils
		print('MODULE: request_adress | USER: {0} | TIME: {1} | PARAMS: {2} | ERROR: {3}'.format(request,
																		datetime.now(),
																		{'snils': snils},
																		str(e) ))		
		
		return HttpResponse(str(e), status=500)	


def request_user_adress(request, snils):
	#запрашивает опекаемых и их адреса, и упаковывает эту информацию в dict
	#output: list [{пациент, адреса пациента:[]}, {пациент, адреса пациента:[]}]

	pacients = request_user_children(request, snils)
	
	if request.session.get('address') == None:
		request.session['address'] = {}

		for pacient in pacients:
			
			adresses = request_adress(request, pacient['SNILS'])
			request.session['address'][pacient['SNILS']] = adresses

	for pacient in pacients:
		pacient['adresses'] = request.session.get('address').get(pacient['SNILS'])		
	
	print(pacients)
	return pacients	

def test(request):
	return sched1(request, '032-524-797 39', '2019-01-01', '2019-01-31', 'one')

if __name__=='__main__':
	a = request_adress(None, '032-524-797 39')

