from django.contrib.auth.models import User

from ipware.ip import get_real_ip


class Middleware(object):
    def process_request(self, request):
        request.log_data = dict(
            ip=get_real_ip(request), user=request.user)
