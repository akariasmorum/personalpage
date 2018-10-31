from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .forms import Message
from datetime import datetime
import http.client as hc
import json
from django.urls import reverse_lazy
from django.views import generic

from .forms import SignUpForm

# Create your views here.
def login(request):
	if 'name' in request.POST:		
		request.session['name'] = request.POST['name']+ ' '+request.POST['surname']
		request.session.save()
		user = {'nickname': request.session['user']}
		
	else:
		return render(request, 'login.html', context = {'title':'Аутентификация'})

def schedule(request):	
	return render(request, 'schedule.html', context={'title': 'Расписание', 'nbar': 'schedule', 'name': (request.user.surname + ' ' + request.user.name) })		

def get_message(request):
	if request.method =='POST':
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

					
	else:
		form=Message()
	return render(request, 'message.html', context={'title': 'Расписание', 'nbar': 'message', 'form': form, 'name': (request.user.surname + ' ' + request.user.name) })

def calldoc(request):
	return render(request, 'calldoc.html', context={'title': 'Вызов врача на дом', 'nbar': 'call-doc', 'name': (request.user.surname + ' ' + request.user.name) })
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


class SignUp(generic.CreateView):
	form_class = SignUpForm
	success_url = reverse_lazy('login')
	template_name = 'signup.html'