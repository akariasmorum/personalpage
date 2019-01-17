from datetime import datetime
import uuid

class auth_esia:
	def __init__(self):
		pass

	def get_scope(self):
		return "http://esia-portal1.test.gosuslugi.ru/sbj_inf"

	def get_timestamp(self):
		return datetime.now().strftime('%Y.%m.%d %H:%M:%S +0500')

	def get_cliendID(self):
		return 'LK_DGKB56_RU'

	def get_client_secret(self):


	def get_redirect_uri(self):
		pass

	def get_response_type(self):
		pass

	def get_state(self):
		return uuid.uuid1()

	def get_client_secret_string(self):
		scope = self.get_scope()
		stamp = self.get_timestamp()
		clientID = self.get_cliendID()
		state = self.get_state()
		return str(scope)+str(stamp)+str(clientID)+str(state)

	def sign_client_secret_string(self):
