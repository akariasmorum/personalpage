from django.shortcuts import render
import http.client as hc
import json

# Create your views here.
def login(request):
	if 'nick' in request.POST:		
		request.session['user'] = request.POST['nick']
		request.session.save()
		user = {'nickname': request.session['user']}
		#return render(request, 'rendered.html', context={'title':'welcome', 'user':user})
	else:
		return render(request, 'login.html', context = {'title':'Аутентификация'})
def schedule(request):	
	return render(request, 'schedule.html', context={'title': 'Расписание', 'nbar': 'schedule'})		
def calldoc(request):
	return render(request, 'calldoc.html', context={'title': 'Вызов врача на дом', 'nbar': 'call-doc'})
def ehr(request):
	return render(request, 'ehr.html', context={'title': 'Электронная медицинская карта', 'nbar': 'ehr'})
def app(request):
	return render(request, 'appointment.html', context={'title': 'Запись на прием', 'nbar': 'app'})			
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
