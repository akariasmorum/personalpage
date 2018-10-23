from django import forms

class Message(forms.Form):
	snils = forms.CharField(label='СНИЛС', max_length=14)
	id_doc_site = forms.CharField(label='ID вставки', max_length=5)
	recipient = forms.CharField(label='Кому обращение', max_length=20)
	subject = forms.CharField(label='Тема сообщения', max_length=20)
	message = forms.CharField(label='Сообщение', max_length=200)
	phone = forms.CharField(label='Телефон', max_length=16)
	email = forms.CharField(label='E-Mail', max_length=20)