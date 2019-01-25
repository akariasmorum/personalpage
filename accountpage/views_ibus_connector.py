from django.http import HttpResponseRedirect, HttpResponse
import http.client as hc
import json
import traceback

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
			
		resp = self.con.getresponse()

		if resp.status!=200:
			raise Exception('Не удалось подключиться к шине!')
		else:	
			decoded_response = resp.read().decode()

			print('decoded_response: {0}'.format(decoded_response))
			js = json.loads(decoded_response)

			return js

def get_check_code(request, snils, code):
	#params_dict = {'snils':snils, 'code':code}
	params_dict = {'snils':'032-524-797 39', 'code':'3941711'}
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