from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.

class PatientUserManager(BaseUserManager):
	def create_user(self, snils, name, surname, telephone, password=None):
		'''Создание пользователя с email, телефоном, датой рождения, и паролем'''
		if not telephone:
			raise ValueError('Отсутствует Номер телефона')
		if not snils:
			raise ValueError('Отсутствует Номер СНИЛС')
		if not name:
			raise ValueError('Отсутствует Имя')
		if not surname:
			raise ValueError('Отсутствует Фамилия')

		user = self.model(snils, name, surname, telephone)
		user.set_password(password)
		user.save(using=self._db)	


class PatientUser(AbstractBaseUser):
	snils = models.CharField('СНИЛС', max_length= 14, unique=True)
	email = models.EmailField('email', max_length= 255, blank=True)
	name = models.CharField('Имя', max_length= 255, blank=True)
	surname = models.CharField('Фамилия', max_length= 50, blank=True)

	patronimic = models.CharField('Отчество', max_length= 255, blank=True)
	
	date_joined = models.DateTimeField('Дата Регистрации', auto_now_add=True)
	telephone = models.CharField('Номер телефона', max_length= 18, blank=True)

	USERNAME_FIELD = 'snils'
	EMAIL_FIELD = 'email'

	REQUIRED_FIELDS = ['name', 'surname', 'telephone']

	objects = PatientUserManager()

	def get_full_name(self):
		'''
		Возвращает first_name и last_name с пробелом между ними.
		'''
		full_name = '%s %s' % (self.name, self.surname)
		return full_name.strip()

	def get_short_name(self):
		'''
		Возвращает сокращенное имя пользователя.
		'''
		return self.name



