from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.forms import ModelForm, ModelChoiceField

from .models import PatientUser, CallDoc, Patient, Message

'''class Message(forms.Form):
	snils = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='СНИЛС', max_length=14)
	id_doc_site = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='ID вставки', max_length=5)
	recipient = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='Кому обращение', max_length=20)
	subject = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='Тема сообщения', max_length=20)
	message = forms.CharField(widget =forms.Textarea(attrs={'class': 'form-control'}),label='Сообщение', max_length=200)
	phone = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='Телефон', max_length=16)
	email = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='E-Mail', max_length=20)

'''
class MessageForm(ModelForm):
	status_send = forms.CharField(    widget = forms.TextInput(attrs={'class': 'form-control','id':'ajax_status'}),label='Статус выполнения Ajax', max_length=10)
	date        = forms.DateTimeField(widget = forms.TextInput(attrs={'class': 'form-control','id':'date_doc'   }),label='Дата')
	id_doc_site = forms.CharField(    widget = forms.TextInput(attrs={'class': 'form-control','id':'id_doc_site'}),label='ID вставки', max_length=50)
	
	recipient   = forms.CharField(    widget = forms.TextInput(attrs={'class': 'form-control','id':'recipient'  }),label='Кому обращение', max_length=20, required = False)
	subject     = forms.CharField(    widget = forms.TextInput(attrs={'class': 'form-control','id':'subject'    }),label='Тема сообщения', max_length=50)
	message     = forms.CharField(    widget = forms.Textarea (attrs={'class': 'form-control','id':'message'    }),label='Сообщение', max_length=200)
	
	def save_data(self, Snils, Post):
		msg = Message()
		
		msg.sender      = PatientUser.objects.get(snils = Snils) #сделать запрос id по user(snils)
		msg.date        = Post.get('date')
		msg.id_doc_site = Post.get('id_doc_site')
		msg.recipient   = Post.get('recipient')
		msg.subject     = Post.get('subject')
		msg.message     = Post.get('message')
		msg.status_send = Post.get('status_send')

		msg.save()

	def return_all(self):
		mes = Message.objects.all()
		return mes
	#выгружаем данные в ДИВ основываясь на снилс
	#phone       = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='Телефон', max_length=16)
	#email       = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='E-Mail', max_length=20)

	class Meta:
		model  = Message
		fields = ['status_send','date', 'id_doc_site', 'recipient', 'subject', 'message']



class SignUpForm(UserCreationForm):
	snils = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'СНИЛС'}), max_length=14, help_text='Номер СНИЛС')
	name = forms.CharField(widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя', 'id': 'inlineFormInputGroup'}), max_length=255, help_text='Ваше имя')
	surname=forms.CharField(widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}), max_length=255, help_text='Фамилия')
	telephone=forms.CharField(widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}), max_length=18, help_text='Введите номер телефона')
	password1=forms.CharField(widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))
	password2=forms.CharField(widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите'}))

	class Meta(UserCreationForm):
		model = PatientUser
		fields = ('snils', 'name', 'surname', 'telephone')

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
