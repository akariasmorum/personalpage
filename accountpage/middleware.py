class Modify(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.get('pacients'):
            if str(request.user) != 'AnonymousUser':
                from .views import request_user_children
                request.session['pacients'] = request_user_children(request.user.snils)

        response = self.get_response(request)
        return response
