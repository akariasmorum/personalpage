from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login, logout

from .forms import Message
from datetime import datetime
import http.client as hc
import json


from .forms import SignUpForm, CallDocForm, Patient, AddChildForm, MessageForm, LoginForm, CallDoctorForm

#
#ЛОГИН
#

def loginView(request):
	if request.method == 'POST':		
		form = LoginForm(request.POST)

		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			login_user = authenticate(username = username, password = password)
			if login_user:
				login(request, login_user)
				return redirect('/schedule')
		
	else:
		form = LoginForm()

	return render(request, 'login.html', context = {'title':'Аутентификация', 'form': form})

#########################



###Расписание#########

def schedule(request):	
	return render(request, 'schedule.html', context={'title': 'Расписание', 'nbar': 'schedule', 'name': (request.user.surname + ' ' + request.user.name) })		

######################




#просмотр детей

class ChildrenView(generic.ListView):
	model = Patient
	context_object_name = 'children'
	template_name = 'mypage.html'

	'''def get_queryset(self):
		return Patient.objects.filter(trustee = self.request.user)
'''
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['children'] = Patient.objects.filter(trustee = self.request.user)
		return context

		
	'''def __init__(self, user, *args, **kwargs):
		super(ChildrenView, self).__init__(*args, **kwargs)
		self.queryset = Patient.objects.filter(trustee = user)'''


#######################




#моя страница #####################

def mypage(request):
	children = Patient.objects.filter(trustee = request.user)
	if request.method =='POST':
		form = AddChildForm(request.POST)
		if form.is_valid():
			form.save(request.user)
	else:
		form = AddChildForm()	
	return render(request, 'mypage.html', 
		context= {'title': 'Моя информация', 'nbar': 'mypage',
		           'name': (request.user.surname + ' ' + request.user.name), 
		       'children': children, 'form': form})


############################



#

def get_message(request):
	if request.method =='POST':
		if request.POST["status_send"] == "false":
			message_form = MessageForm(request.POST)
			if message_form.is_valid():
				#return HttpResponse("date type is{0}".format(message_form.return_type()))
				message_form.save_data(request.user.snils, request.POST)
				#return render(request, 'test.html', {'messages':message_form.return_all()})				
				

	form = MessageForm()
	return render(request, 'message.html', 
			   context={'title': 'Расписание', 'nbar': 'message', 
			             'form': form, 
			             'name': (request.user.surname + ' ' + request.user.name), 
		             'my_email': 'email@email.ru',
		             'my_phone': '+7(987)123-32-23',
		               'hidden': ['status_send','date','id_doc_site']
		             })



def calldoc(request):
	if request.method =='POST':
		if request.POST["status_send"] == "false":
			form = CallDoctorForm(request.POST)
			if form.is_valid():
				form.save_data(request.user.snils, request.POST)
				#return render(request, 'test.html', {'answer':form.all()})
			#form.save_data(request.user.snils, request.POST)
			
			'''if form.is_valid():
				
				return HttpResponse("OK")
			else:
				return HttpResponse("NE OK")'''
				
			
	form = CallDoctorForm()
	return render(request, 'calldoc.html', 
		 context={'title': 'Вызов врача на дом', 'nbar': 'call-doc',
		           'form': form, 
		           'name': (request.user.surname + ' ' + request.user.name),
		       'my_email': 'email@email.ru',
		       'my_phone': '+7(987)123-32-23',
				 'hidden': ['status_send', 'date', 
				            'id_doc_site', 'kladr' ,
				                 'house' , 'room']
		         })

	'''
def return_message_page(request):
	form = MessageForm()
	return render(request, 'message.html', 
			   context={'title': 'Расписание', 'nbar': 'message', 
			             'form': form, 
			             'name': (request.user.surname + ' ' + request.user.name), 
		             'my_email': 'email@email.ru',
		             'my_phone': '+7(987)123-32-23',
		               'hidden': ['status_send','date','id_doc_site']
		             })

	if request.method =='POST':
		
	else:
		return_message_page(request)
		if request.POST["status_send"] == "false":
			
		
		#return HttpResponse("{0}".format(json.dumps(request.POST)))
		
		form = Message(request.POST)
		if form.is_valid():
			try:
				con = hc.HTTPConnection('ibus.dgkb.lan', 80) 
				headers = { 
				'Authorization': 'Basic cm9vdDpyb290', 
				'Host': 'localhost:5000', 
				'Content-Type': 'application/json' 
				} 
				
				dic = {
						"snils": form.cleaned_data['snils'],
						"id_doc_site": form.cleaned_data['snils'],
						#"datedoc": datetime.now().strftime('%Y-%m-%d %H:%M'),
						"datedoc": datetime.now().strftime('%Y-%m-%d %H:%M'),
						"recipient": form.cleaned_data['recipient'],
						"subject": form.cleaned_data['subject'],
						"message": form.cleaned_data['message'],
						"phone":   form.cleaned_data['phone'],
						"email":   form.cleaned_data['email'],
					}
				parametr = str(json.dumps(dic)) 

				

				body = json.dumps({ 
				'name': 'MessagePacientNew', 
				'params': {'request': parametr} 
				}) 

				con.request('POST', '/api/executescript', body=body, headers=headers) 

				c = con.getresponse().read().decode() 
				
				return HttpResponse(dic['datedoc'] + " " + str(c))
			except Exception as ex:
				return HttpResponse(str(ex))	

					'''			
	




def ehr(request):
	return render(request, 'ehr.html', context={'title': 'Электронная медицинская карта', 'nbar': 'ehr', 'name': (request.user.surname + ' ' + request.user.name) })
def app(request):
	return render(request, 'appointment.html', context={'title': 'Запись на прием', 'nbar': 'app', 'name': (request.user.surname + ' ' + request.user.name) })			
def calendar(request):
	con = hc.HTTPConnection('ibus.dgkb.lan', 80) 
	headers = { 
	'Authorization': 'Basic cm9vdDpyb290', 
	'Host': 'localhost:5000', 
	'Content-Type': 'application/json' 
	} 

	parametr = str(json.dumps({'snils': '123123123'})) 

	

	body = json.dumps({ 
	'name': 'CalendarList', 
	'params': {'request': parametr} 
	}) 

	con.request('POST', '/api/executescript', body=body, headers=headers) 

	c = con.getresponse().read().decode() 
	a = json.loads(c)

	x= json.loads(a['output']['CalendarList'])

	data = []
	for dates in x:
		first = [dates['NRU_GROUP'], dates['datedoc']]
		data.append(first)
		

	return render(request, 'calendar.html', context = {'title': 'Календарь пациента', 'nbar': 'calendar', 'data':  data})

#выход из системы	
def user_logout(request):
	logout(request)
	return redirect('login')


class SignUp(generic.CreateView):
	form_class = SignUpForm
	success_url = reverse_lazy('login')
	template_name = 'signup.html'

