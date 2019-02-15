from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import http.client as hc
import json
import time

def sched1(request):
	con = hc.HTTPConnection('10.130.4.219', '8000')
	headers = {
			'Authorization': 'Basic cm9vdDpyb290',
			'Host': 'localhost' + ':' + '8000',
			'Content-Type': 'application/json'
			}
	parameter = str(json.dumps({
			"snils": request.POST.get('snils'),
			"date_begin": request.POST.get('date_begin'),
			"date_end": request.POST.get('date_end'),
			"amount": "one",
		}))
	print(parameter)

	body = json.dumps({
		'name': 'CalendarList',
		'params': {'request': parameter}
		})		
	start = time.time()
	con.request(
			'POST',
			'', 
			body=body,
			headers=headers)		
	end = time.time()
	print("TEST_POST_RESPONSE %s seconds ---" % (end - start))			
	resp = con.getresponse()
	
	data = json.loads(resp.read().decode('utf-8'))	
	print(data)

	return JsonResponse(data['CalendarList'], safe=False)
	
		