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

class Auth_esia:

	def __init__(self):
		self.scope = self.get_scope()
		self.stamp = self.get_timestamp()
		self.clientID = self.get_cliendID()
		self.state = self.get_state()

	def get_scope(self):
		#return "https://esia-portal1.test.gosulsugi.ru/rs/sbjs"
		return 'snils'

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
		'''
		with open(certificates, 'r') as f:
			print(name + ": " + f.read())
			return sert
		'''
	def _load_private_key(self):
		return self._load_sertificate('private.key')

	def _load_public_sertificate(self):
		return self._load_sertificate('certificate.crt')

	def _sign_PKCS7_message(self, text):
		'''Подписать text в формате PKCS#7


		cert_buf = None
		key_buf = None
		try:
			cert_buf = self._load_public_sertificate()

			key_buf = self._load_private_key()

		except Exception as ex:
			print(print(ex))


		pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key_buf)
		signcert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_buf)

		bio_in = crypto._new_mem_buf(text.encode())
		PKCS7_NOSIGS = 0x4  # defined in pkcs7.h
		pkcs7 = crypto._lib.PKCS7_sign(signcert._x509, pkey._pkey, crypto._ffi.NULL, bio_in, PKCS7_NOSIGS)  # noqa
		bio_out = crypto._new_mem_buf()
		crypto._lib.i2d_PKCS7_bio(bio_out, pkcs7)
		sigbytes = crypto._bio_to_string(bio_out)

		return sigbytes'''
		source_path = ""
		with tempfile.NamedTemporaryFile(mode='w', delete=False) as source_file:

			source_file.write(text)
			source_path = source_file.name

		destination_path = ""
		with tempfile.NamedTemporaryFile(mode='wb', delete=False) as destination_file:

			destination_path = destination_file.name

		cmd = 'openssl smime -sign -md sha256 -in {f_in} -signer {cert} -inkey {key} -out {f_out} -outform DER'
		# You can verify this signature using:
		# openssl smime -verify -inform DER -in out.msg -content msg.txt -noverify \
		# -certfile ../key/septem_sp_saprun_com.crt

		os.system(cmd.format(
			f_in=source_path,
			cert=self._load_public_sertificate(),
			key=self._load_private_key(),
			f_out= destination_path,
		))


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
		r = requests.post('https://esia-portal1.test.gosuslugi.ru/aas/oauth2/te', data = self.params)
		return r


	def generate_uri(self):
		#url = "https://esia-portal1.test.gosuslugi.ru?"
		url = "https://esia-portal1.test.gosuslugi.ru/aas/oauth2/ac?"

		url += urlencode(self.generate_params())
		return url

	def _request_user_data(self, resource_id, access_token, oid):
		url = 'https://esia-portal1.test.gosuslugi.ru/{resource_id}/{oid}'.format(resource_id = resource_id, oid = oid)
		headers = {'Authorization': 'Bearer ' + access_token}
		req = requests.get(url, headers=headers)
		return req.text

	def request_user_snils(self, access_token, oid):
		req = self._request_user_data('rs/prns', access_token, oid)
		data = json.loads(req)
		return data['snils']


if __name__ == "__main__":
	a = Auth_esia()
	print(a.generate_access_token_params('xyz'))
