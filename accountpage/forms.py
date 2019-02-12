from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.forms import ModelForm, ModelChoiceField
import json

from .models import PatientUser, CallDoc, Patient, Message, CallDoctor
from .views_ibus_connector import get_check_code


class LoginForm(forms.Form):
	username = forms.CharField(label='Введите Ваш СНИЛС', widget = forms.TextInput(attrs={'class': 'form-control','id':'id_username', 'placeholder': 'Введите Ваш СНИЛС'}), max_length=14)
	password = forms.CharField(label='Введите Ваш пароль', widget = forms.PasswordInput(attrs={'class': 'form-control' , 'placeholder': 'Введите пароль'}))
	
	def clean(self):
		cleaned_data = super(LoginForm, self).clean()
		username = self.cleaned_data['username']
		password = self.cleaned_data['password']
		try:
			PatientUser.objects.filter(snils=username).exists()
			user = PatientUser.objects.get(snils=username)
			if user and not user.check_password(password):
				self.add_error('password', 'Неверный пароль!')
		except Exception as errS:
			self.add_error('username', 'Пользователь с таким СНИЛС не зарегистрирован!')


		


class MessageForm(ModelForm):
	#status_send = forms.CharField(    widget = forms.TextInput(attrs={'class': 'form-control','id':'ajax_status'}),label='Статус выполнения Ajax', max_length=10)
	date      = forms.DateTimeField(  widget = forms.HiddenInput(attrs={'id':'date_doc'   }), label='Дата')
	id_doc_site = forms.CharField(    widget = forms.HiddenInput(attrs={'id':'id_doc_site'}), label='ID вставки',  max_length=50)
	
	recipient   = forms.CharField(    widget = forms.TextInput(attrs={'class': 'form-control','id':'recipient'  }), label='Кому обращение', max_length=100, min_length = 4)
	subject     = forms.CharField(    widget = forms.TextInput(attrs={'class': 'form-control','id':'subject'    }), label='Тема сообщения', max_length=100, min_length = 4)
	message     = forms.CharField(    widget = forms.Textarea (attrs={'class': 'form-control','id':'message'    }), label='Сообщение',      max_length=500, required = True, min_length = 10)
	phone 		= forms.CharField(	  widget = forms.TextInput(attrs={'class': 'form-control','id':'phone'	}), label='Номер телефона', max_length=16, required = True, min_length = 16)
	
	

	def save_data(self, Snils, Post):
		msg = Message()
		
		msg.sender      = PatientUser.objects.get(snils = Snils) #сделать запрос id по user(snils)
		
		msg.date        = Post.get('date'    	)
		msg.id_doc_site = Post.get('id_doc_site')
		msg.recipient   = Post.get('recipient'  )
		msg.subject     = Post.get('subject'    )
		msg.message     = Post.get('message'    )
		msg.phone 		= Post.get('phone'		)
		#msg.status_send = Post.get('status_send')

		msg.save()

	def return_all(self):
		mes = Message.objects.all()
		return mes
	
	class Meta:
		model  = Message
		fields = ['date',  'id_doc_site', 'recipient', 'subject', 'message', 'phone']


class CallDoctorForm(forms.Form):
	
	date         = forms.DateTimeField(widget = forms.TextInput(attrs={'id':'date_doc'   }),label='Дата')
	id_doc_site  = forms.CharField    (widget = forms.TextInput(attrs={'id':'id_doc_site'}),label='ID вставки', max_length=50)
	#patient      = forms.CharField    (widget = forms.Select   (attrs={'class': 'form-control','id':'pacient'   }),label='Пациент')
	adress       = forms.CharField    (widget = forms.Select   (attrs={'class': 'form-control', 'id': 'select_address'}), label='Адрес пациента')
	temperature  = forms.ChoiceField  (widget = forms.Select   (attrs={'class': 'form-control'}),label='Температура', choices = ((str(x*0.1)[:4], str(x*0.1)[:4]) for x in range(360, 401)))
	complaints   = forms.CharField    (widget = forms.Textarea (attrs={'class': 'form-control'}),label='Жалобы', max_length=1000, min_length = 4, required = True)

	add_inform   = forms.CharField    (widget = forms.Textarea (attrs={'class': 'form-control addition','id':'add_inform'}),label='Дополнительная информация', max_length=1000, required = False)
	telephone 	 = forms.CharField 	  (widget = forms.TextInput(attrs={'class': 'form-control', 'id': 'telephone'}), label = 'Номер телефона', max_length = 16, min_length = 16,  required = True)
	#kladr 		 = forms.CharField	  (widget = forms.TextInput(attrs={'class': 'form-control d-none', 'id': 'kladr'}))
	#home 		 = forms.CharField	  (widget = forms.TextInput(attrs={'class': 'form-control d-none', 'id': 'kladr'}))
	#kv  		 = forms.CharField	  (widget = forms.TextInput(attrs={'class': 'form-control d-none', 'id': 'kladr'}))

	

	'''def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super(CallDoctorForm, self).__init__(*args, **kwargs)
		self.fields['patient'] = forms.ChoiceField(widget = forms.Select(attrs={'class': 'form-control','id':'pacient'}),label='Пациент', choices = self.patients_list(user))
		self._user = user'''

	def snils_to_patient(self, Snils):
		self.fields['patient'] = forms.ModelChoiceField(queryset = Patient.objects.filter(snils = Snils))
		#initial = Patient.objects.get(snils = Snils))#Patient.objects.get(snils = Snils)
		#self.fields['patient'].disabled = False

	def save_data(self, Snils, Post):
		callDoctor = CallDoctor()

		callDoctor.trustee = PatientUser.objects.get(snils = Snils)
		#callDoctor.patient = Patient.    objects.get(snils = Post['patient'])
		callDoctor.patient     = Post.get('patient'    )
		callDoctor.date        = Post.get('date'       )
		callDoctor.id_doc_site = Post.get('id_doc_site')
		callDoctor.temperature = Post.get('temperature')
		callDoctor.complaints  = Post.get('complaints' )
		callDoctor.kladr       = Post.get('kladr'      )
		callDoctor.house       = Post.get('house'      )
		callDoctor.room        = Post.get('room'       )
		callDoctor.add_inform  = Post.get('add_inform' )
		callDoctor.status_send = Post.get('status_send')

		callDoctor.save()

	def all(self):
		return CallDoctor.objects.all()		

	def patients_list(self, user):
		patients = Patient.objects.filter(trustee = user)
		pl       = [ ( patient.return_snils(), patient ) for patient in patients ]
		return pl
	

class SignUpForm(UserCreationForm):
	error_messages = {
		'password_mismatch': ("Пароли не совпадают!"),
		'password_entirely_numeric': ('Ваш пароль состоит только цифр. Добавьте и буквы'),
		
	}

	snils =   forms.CharField(widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'СНИЛС'}), max_length=14, help_text='Номер СНИЛС', error_messages={'required': 'Введите СНИЛС!'})
	name =    forms.CharField(widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя', 'id': 'inlineFormInputGroup'}), max_length=255, help_text='Ваше имя', error_messages={'required': 'Введите Имя!'})
	surname=  forms.CharField(widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}), max_length=255, help_text='Фамилия', error_messages={'required': 'Введите Фамилию!'})
	telephone=forms.CharField(widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}), max_length=18, help_text='Введите номер телефона', error_messages={'required': 'Введите номер телефона!'})
	regcode  =forms.CharField(widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Регистрационный код'}), max_length=18, help_text='Введите Регистрационный код', error_messages={'required': 'Введите регистрационный код!'})
	password1=forms.CharField(widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}), error_messages = {'requied': 'Введите Пароль!', } )
	password2=forms.CharField(widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите'}), error_messages = {'requied': 'Повторите Пароль!', 'password_entirely_numeric': 'Ваш пароль состоит только цифр. Добавьте и буквы'})

	class Meta(UserCreationForm):
		model = PatientUser
		fields = ('snils', 'name', 'surname', 'telephone')


	#проверка СНИЛС на уникальность

	def clean_snils(self):
		snils = self.cleaned_data.get("snils")

		if PatientUser.objects.filter(snils=snils).exists():
			#Если такой СНИЛС уже есть, то вывести ошибку
			self.add_error('snils', 'Пользователь с таким СНИЛС уже существует!')
		else:
			return snils

	def clean_regcode(self):

		reg = self.cleaned_data.get('regcode')
		print('Запрашиваю регистрационный код: {0} {1}'.format(reg, self.cleaned_data.get('snils')))

		check_code = None

		try:
			check_code = get_check_code(None, self.cleaned_data.get('snils'), reg)
			if check_code == None:
				self.add_error('regcode', 'Вы не давали согласие')			

			elif reg != check_code:
				self.add_error('regcode', 'Не правильный регистрационный код!')	
		except Exception as Check_code_ex:
			print(Check_code_ex)
			self.add_error('regcode', 'Ошибка проверки регистрационного кода, проверьте правильноcть указанного СНИЛС')

		

			

class AddChildForm(ModelForm):
	name = forms.CharField(label='Имя', widget =forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}), max_length=50, help_text='Имя опекаемого')
	surname= forms.CharField(label='Фамилия', widget =forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}), max_length=80, help_text='Фамилия опекаемого')
	patronimic = forms.CharField(label='Отчество', widget =forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}), max_length=80, help_text='Отчество опекаемого')
	snils = forms.CharField(label='СНИЛС', widget =forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'СНИЛС'}), max_length=14, help_text='СНИЛС опекаемого')
	date_born = forms.DateField(label='Дата Рождения', widget =forms.TextInput(attrs={'class': 'form-control'}))

	class Meta:
		model = Patient
		fields = ['name', 'surname', 'patronimic', 'snils', 'date_born']

	def save(self, user, commit=True):
		instance = super(AddChildForm, self).save(commit=False)
		instance.trustee = user
		if commit:
			instance.save()
			self.save_m2m()
		return instance		

class CallDocForm(ModelForm):
	temperature = forms.ChoiceField(widget = forms.Select(attrs={'class': 'form-control'}),label='Температура', choices = ((str(x*0.1)[:4], str(x*0.1)[:4]) for x in range(360, 401)))
	complaints = forms.CharField(widget =forms.Textarea(attrs={'class': 'form-control'}),label='Жалобы', max_length=1000)


	def __init__(self, user, *args, **kwargs):
		super(CallDocForm, self).__init__(*args, **kwargs)
		self.fields['patient'] = forms.ModelChoiceField(queryset = Patient.objects.filter(trustee = user), widget = forms.Select(attrs={'class': 'form-control'}),label='Пациент')
		self._user = user

	def save(self, commit=True):
		instance = super(CallDocForm, self).save(commit=False)
		instance.trustee = self._user
		if commit:
			instance.save()
			self.save_m2m()
		return instance
			
	class Meta:
		model = CallDoc
		fields = ['patient','temperature','complaints']
