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

	def __str__(self):
		return "{0} {1}".format(self.surname, self.name)

	def return_snils(self):
		return "{0}".format(self.snils)
	


class CallDoc(models.Model):	
	date = models.DateTimeField('Время вызова', auto_now_add=True)
	patient = models.ForeignKey(Patient, models.CASCADE)
	trustee = models.ForeignKey(PatientUser, models.CASCADE)
	temperature = models.CharField('Температура', max_length=4)
	complaints = models.CharField('Жалобы', max_length=1000)


class CallDoctor(models.Model):
	trustee     = models.ForeignKey   (PatientUser, models.CASCADE)
	patient     = models.CharField    ('СНИЛС'          , max_length= 14)

	id_doc_site = models.CharField    ('ID сайта'       , max_length=50  )
	date        = models.DateTimeField('Дата обращения' )
	temperature = models.CharField    ('Температура'    , max_length=4   )
	complaints  = models.CharField    ('Жалобы'         , max_length=1000)

	kladr       = models.CharField    ('КЛАДР'          , max_length=17  )
	house       = models.CharField    ('Дом'            , max_length=10  )
	room        = models.CharField    ('Квартира'       , max_length=10  , blank=True)
	add_inform  = models.CharField    ('Доп.Информация' , max_length=1000, blank=True)
	status_send = models.CharField    ('Статус отправки', max_length=10  )


class Message(models.Model):	 
	sender      = models.ForeignKey   (PatientUser, models.CASCADE)
	date        = models.DateTimeField('Дата обращения' )#, auto_now_add=True)
	id_doc_site = models.CharField    ('ID сайта'       , max_length=50)
	recipient   = models.CharField    ('Кому обращение' , max_length=50)
	subject     = models.CharField    ('Тема сообщения' , max_length=50)
	message     = models.CharField    ('Сообщение'      , max_length=100)
	status_send = models.CharField    ('Статус отправки', max_length=10)	
	phone   	= models.CharField    ('Номер телефона' , max_length=16)

	

"""	
    snils = forms.CharField(,label='СНИЛС', max_length=14)
	id_doc_site = forms.CharField(label='ID вставки', max_length=5)
	recipient = label='Кому обращение', max_length=20)
	subject = label='Тема сообщения', max_length=20)
	message = label='Сообщение', max_length=200)
	phone = label='Телефон', max_length=16)
	email = label='E-Mail', max_length=20)

	
"""

