from django.http import HttpResponseRedirect, HttpResponse
import http.client as hc
import json

def sched1(request):
	con = hc.HTTPConnection('10.130.4.219', '8000')
	headers = {
			'Authorization': 'Basic cm9vdDpyb290',
			'Host': 'localhost' + ':' + '8000',
			'Content-Type': 'application/json'
			}
	parameter = str(json.dumps({
			"snils": "032-545-797 39",
			"date_begin": "2019-01-01",
			"date_end": "2019-01-31",
			"amount": "one",
		}))

	body = json.dumps({
		'name': 'CalendarList',
		'params': {'request': parameter}
		})		

	con.request(
			'POST',
			'', 
			body=body,
			headers=headers)		
			
	resp = con.getresponse()

	decoded_response = resp.read()

	print('decoded_response: {0}'.format(decoded_response))
		