key = "6Ldd07ogAAAAACktG1QNsMTcUWuwcwtkneCnPDOL"

from urllib.parse import urlencode
from urllib.request import urlopen
import json


URIReCaptcha = 'https://www.google.com/recaptcha/api/siteverify'
recaptchaResponse = body.get('recaptchaResponse', None)
        private_recaptcha = '6LdXXXXXXXXXXXXXXXXXXXXXXXX'
        remote_ip = request.remote_addr
        params = urlencode({
            'secret': private_recaptcha,
            'response': recaptchaResponse,
            'remoteip': remote_ip,
        })

        # print params
        data = urlopen(URIReCaptcha, params.encode('utf-8')).read()
        result = json.loads(data)
        success = result.get('success', None)

        if success == True:
            print('reCaptcha passed')
        else:
            print('recaptcha failed')
