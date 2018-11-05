from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from .models import PatientUser 

class Message(forms.Form):
	snils = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='СНИЛС', max_length=14)
	id_doc_site = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='ID вставки', max_length=5)
	recipient = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='Кому обращение', max_length=20)
	subject = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='Тема сообщения', max_length=20)
	message = forms.CharField(widget =forms.Textarea(attrs={'class': 'form-control'}),label='Сообщение', max_length=200)
	phone = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='Телефон', max_length=16)
	email = forms.CharField(widget =forms.TextInput(attrs={'class': 'form-control'}),label='E-Mail', max_length=20)


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

	