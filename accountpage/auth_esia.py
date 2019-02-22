from django.shortcuts import render, redirect
from datetime import datetime
#from OpenSSL import crypto
from urllib.parse import urlencode
import uuid
import base64
from pathlib import Path
import os
import tempfile
import pytz
import json
import requests
from django.conf import settings
from .models import PatientUser
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from .views_ibus_connector import is_user_accepted_permissions

class Auth_esia:

	def __init__(self):
		self.url = settings.AUTH_ESIA_ADDRESS
		self.scope = self.get_scope()
		self.stamp = self.get_timestamp()
		self.clientID = self.get_cliendID()
		self.state = self.get_state()

	def get_scope(self):
		#return "https://esia-portal1.test.gosulsugi.ru/rs/sbjs"
		return 'snils fullname'

	def get_timestamp(self):
		return datetime.now(pytz.timezone('Asia/Yekaterinburg')).strftime('%Y.%m.%d %H:%M:%S %z').strip()

	def get_cliendID(self):
		return 'LK_DGKB56_RU'

	def get_access_type(self):
		return 'offline'


	def get_client_secret(self):
		string = self._get_client_secret_string()
		sign = self._sign_PKCS7_message(string)
		based64string = self.convert_to_base64(sign).decode("utf-8")
		return based64string

	def get_redirect_uri(self):
		#return "lk.dgkb56.ru"
		return 'http://lk.dgkb56.ru/esia_callback'

	def get_response_type(self):
		return 'code'

	def get_state(self):
		return uuid.uuid4()
		#return "699c651a-1ae6-11e9-bda0-21a8af725518"

	def _get_client_secret_string(self):

		secret = str(self.scope)+str(self.stamp)+str(self.clientID)+str(self.state)

		return secret


	def _load_sertificate(self, name):
		sert = None

		certificates = Path(__file__).resolve().parent / 'certificates' / name

		return certificates

	def _load_private_key(self):
		return self._load_sertificate('private.key')

	def _load_public_sertificate(self):
		return self._load_sertificate('certificate.crt')

	def _sign_PKCS7_message(self, text):
		'''Подписать text в формате PKCS#7'''

		#Создаем входной Temp File, куда записываем текст
		source_path = ""
		with tempfile.NamedTemporaryFile(mode='w', delete=False) as source_file:

			source_file.write(text)
			source_path = source_file.name

		#Создаем Выходной temp file, куда записываем результат подписи
		destination_path = ""
		with tempfile.NamedTemporaryFile(mode='wb', delete=False) as destination_file:

			destination_path = destination_file.name

		cmd = 'openssl smime -sign -md sha256 -in {f_in} -signer {cert} -inkey {key} -out {f_out} -outform DER'
		# You can verify this signature using:
		# openssl smime -verify -inform DER -in out.msg -content msg.txt -noverify \
		# -certfile ../key/septem_sp_saprun_com.crt
		#Выполнить команду
		os.system(cmd.format(
			f_in=source_path,
			cert=self._load_public_sertificate(),
			key=self._load_private_key(),
			f_out= destination_path,
		))

		#Считываем выходной temp файл
		raw_client_secret = open(destination_path, 'rb').read()

		return raw_client_secret





	def convert_to_base64(self, message):
		return base64.urlsafe_b64encode(message)

	def generate_params(self):
		self.params = {}
		self.params["client_id"] = self.clientID
		self.params["client_secret"]=self.get_client_secret()
		self.params["redirect_uri"]=self.get_redirect_uri()
		self.params["scope"]= self.scope
		self.params["response_type"]=self.get_response_type()
		self.params["state"]=self.state
		self.params["timestamp"]=self.stamp
		self.params["access_type"]=self.get_access_type()

		return self.params

	def generate_access_token_params(self, auth_code):

		self.params = {}

		self.params["client_id"] = self.clientID
		self.params["code"] = auth_code
		self.params["grant_type"] = "authorization_code"
		self.params["client_secret"]=self.get_client_secret()
		self.params["state"]=self.state
		self.params["redirect_uri"]=self.get_redirect_uri()
		self.params["scope"]= self.scope
		self.params["timestamp"]=self.stamp
		self.params["token_type"]="Bearer"

		return self.params

	def post_access_token_params(self):
		r = requests.post('{url}aas/oauth2/te'.format(url=self.url), data = self.params)
		return r


	def generate_uri(self):
		#url = "https://esia-portal1.test.gosuslugi.ru?"
		url = "{url}aas/oauth2/ac?".format(url = self.url)

		url += urlencode(self.generate_params())
		return url

	def _request_user_data(self, resource_id, access_token, oid):
		url = '{url}{resource_id}/{oid}'.format(url = self.url, resource_id = resource_id, oid = oid)
		headers = {'Authorization': 'Bearer ' + access_token}
		req = requests.get(url, headers=headers)
		return req.text

	def request_user_snils(self, access_token, oid):
		req = self._request_user_data('rs/prns', access_token, oid)
		data = json.loads(req)
		print('request-esia: {0}'.format(data))
		return data['snils']

	def request_user_snils_name_surname(self, access_token, oid):
		req = self._request_user_data('rs/prns', access_token, oid)
		data = json.loads(req)
		print('request-esia: {0}'.format(data))
		return data['snils'], data['firstName'], data['lastName']


def redirect_esia(request):
	auth = Auth_esia()
	url = auth.generate_uri()

	return redirect(url)

def get_or_create_patient(snils, name, surname):
	patient = None
	try:
		patient = PatientUser.objects.get(snils = snils)
	except Exception as GetPatientEx:
		pass

	if patient == None:
		try:
			print('get_or_create_snils')
			print(snils)
			patient = PatientUser(snils=str(snils), name=name, surname=surname, telephone = '88005553535')
			patient.set_unusable_password()
			patient.save()			

		except Exception as e:
			print(e)
			raise e	
	print("get_or_create")
	print(patient)
	return patient		


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
		#будет кратна 4
		encoded_data += '=' * (-len(encoded_data) % 4)


		decoded = base64.urlsafe_b64decode(encoded_data)
		decoded_json = json.loads(decoded)
		oid = str(decoded_json['urn:esia:sbj_id'])

		#запрос снилса пациента по указанному OID
		snils, name, surname = auth.request_user_snils_name_surname(access_token, oid)

		print ('snils {0} name {1} surname {2}'.format(snils, name, surname))

		try:
			patient = get_or_create_patient(snils, name, surname)
		except Exception:
			raise Exception('Не удалось создать пользователя')
		#Получаем пациента по возвращенному с ЕСИА СНИЛСу
		
		if is_user_accepted_permissions(snils):
			login(request, patient)
			return redirect('/main')
		else:
			return HttpResponse('<h2>Пользователь с таким СНИЛС не давал согласие на обработку персональных данных!</h2>')	

	elif 'access_token' in request.GET:

		return HttpResponse('<h2>Hello TOKEN: {0}</h2>'.format(request.GET.get('access_token')))

		


if __name__ == "__main__":
	a = Auth_esia()
	print(a.generate_access_token_params('xyz'))
