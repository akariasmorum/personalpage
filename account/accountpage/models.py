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
	name = models.CharField('Имя', max_length= 50, blank=True)
	surname = models.CharField('Фамилия', max_length= 80, blank=True)

	patronimic = models.CharField('Отчество', max_length= 80, blank=True)
	
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

class Patient(models.Model):
	name = models.CharField('Имя опекаемого', max_length=50)
	surname = models.CharField('Фамилия опекаемого', max_length=80)
	patronimic = models.CharField('Отчество опекаемого', max_length=80)
	snils = models.CharField('СНИЛС опекаемого', max_length=14)
	date_born = models.DateField('Дата Рождения')
	trustee = models.ForeignKey(PatientUser, models.CASCADE)


class CallDoc(models.Model):	
	date = models.DateTimeField('Время вызова', auto_now_add=True)
	patient = models.ForeignKey(Patient, models.CASCADE)
	trustee = models.ForeignKey(PatientUser, models.CASCADE)
	temperature = models.CharField('Температура', max_length=4)
	complaints = models.CharField('Жалобы', max_length=1000)

	
	


