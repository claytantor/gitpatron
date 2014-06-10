import urllib2
import json
from django.conf import settings
import hashlib
import hmac
import time

# GET /api/v1/account/balance HTTP/1.1
# Accept: */*
# User-Agent: Python
# ACCESS_KEY: <YOUR-API-KEY>
# ACCESS_SIGNATURE: <YOUR-COMPUTED-SIGNATURE>
# ACCESS_NONCE: <YOUR-UPDATED-NONCE>
# Connection: close
# Host: coinbase.com
class CoinbaseV1():

    def refresh_token(
            self,
            access_token,
            refresh_token,
            app_client_id,
            app_client_secret):

        opener = urllib2.build_opener()
        refresh_body = {
            'grant_type':'refresh_token',
            'refresh_token':refresh_token,
            'client_id':app_client_id,
            'client_secret':app_client_secret
        }

        print refresh_body

        refresh_response = opener.open(urllib2.Request(
            'https://coinbase.com/oauth/token',
            json.dumps(refresh_body),
            {'Content-Type': 'application/json'}))

        response_string = refresh_response.read()

        print response_string

        return json.loads(response_string)


    # this really neads to be refactored to always return an object
    # so that the client refresh can have control over the model.
    def get_http_oauth(
            self,
            url,
            access_token,
            refresh_token,
            app_client_id,
            app_client_secret,
            body=None,
            count=0):

        opener = urllib2.build_opener()

        try:
            response_stream = opener.open(urllib2.Request('{0}?access_token={1}'.format(url,access_token),body,{'Content-Type': 'application/json'}))

            #return the valid access token, this will be updated if needed to be refreshed
            response_string = response_stream.read()
            response_object = json.loads(response_string)
            response_object['access_token'] = access_token
            response_object['refresh_token'] = refresh_token
            response_object['error_code'] = None

            return response_object

        except urllib2.HTTPError as e:
            return {'error_code':e.code,'message':'HTTP Error'}


    def get_http(
            self,
            url,
            body=None,
            access_key=settings.COINBASE_API_KEY,
            access_secret=settings.COINBASE_API_SECRET):

        opener = urllib2.build_opener()
        nonce = int(time.time() * 1e6)
        message = str(nonce) + url + ('' if body is None else body)
        signature = hmac.new(access_secret, message, hashlib.sha256).hexdigest()
        opener.addheaders = [('ACCESS_KEY', access_key),
                             ('ACCESS_SIGNATURE', signature),
                             ('ACCESS_NONCE', nonce)]
        try:
            response = opener.open(urllib2.Request(url,body,{'Content-Type': 'application/json'}))
            return response
        except urllib2.HTTPError as e:
            print e
            return e

    def get_json(self, url,
                 body=None,
                 access_key=settings.COINBASE_API_KEY,
                 access_secret=settings.COINBASE_API_SECRET):
        response = self.get_http(url,body,access_key,access_secret)
        json_response = response.read()
        return json.loads(json_response)

    def post_json(self, url, data_obj,
                 access_key=settings.COINBASE_API_KEY,
                 access_secret=settings.COINBASE_API_SECRET):
        response = self.get_http(url,json.dumps(data_obj),access_key,access_secret)
        json_response = response.read()
        return json.loads(json_response)


# REQUEST
# {
#   "button": {
#     "name": "test",
#     "type": "buy_now",
#     "price_string": "1.23",
#     "price_currency_iso": "USD",
#     "custom": "Order123",
#     "callback_url": "http://www.example.com/my_custom_button_callback",
#     "description": "Sample description",
#     "type": "buy_now",
#     "style": "custom_large",
#     "include_email": true
#   }
# }

# Response
# {
#   "success": true,
#   "button": {
#     "code": "93865b9cae83706ae59220c013bc0afd",
#     "type": "buy_now",
#     "style": "custom_large",
#     "text": "Pay With Bitcoin",
#     "name": "test",
#     "description": "Sample description",
#     "custom": "Order123",
#     "callback_url": "http://www.example.com/my_custom_button_callback",
#     "price": {
#       "cents": 123,
#       "currency_iso": "USD"
#     }
#   }
# }
    def post_button_oauth(self,
            button_obj,
            access_token,
            refresh_token,
            app_client_id,
            app_secret_id):
        response_object = self.get_http_oauth('https://coinbase.com/api/v1/buttons',
                                       access_token,
                                       refresh_token,
                                       app_client_id,
                                       app_secret_id,
                                       json.dumps(button_obj))
        return response_object



# Redirect the user to this page
# https://coinbase.com/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_CALLBACK_URL
    def get_oauth_redirect(self):
        return 'https://coinbase.com/oauth/authorize?response_type=code&client_id={0}&redirect_uri={1}'.format(
            settings.COINBASE_OAUTH_CLIENT_ID,
            settings.COINBASE_OAUTH_CLIENT_CALLBACK)

# Initiate a POST request to get the access token
# https://coinbase.com/oauth/token?grant_type=authorization_code&code=CODE&redirect_uri=YOUR_CALLBACK_URL&client_id=CLIENT_ID&client_secret=CLIENT_SECRET
    def get_oauth_response(self,code):
        post_url = 'https://coinbase.com/oauth/token?grant_type=authorization_code' \
                   '&code={0}&' \
                   'redirect_uri={1}&' \
                   'client_id={2}' \
                   '&client_secret={3}'.format(
            code,
            settings.COINBASE_OAUTH_CLIENT_CALLBACK,
            settings.COINBASE_OAUTH_CLIENT_ID,
            settings.COINBASE_OAUTH_CLIENT_SECRET
        )

        response = self.get_http(post_url,'{}')

        # Response containing the 'access_token'
        # {
        #     "access_token": "...",
        #     "refresh_token": "...",
        #     "token_type": "bearer",
        #     "expire_in": 7200,
        #     "scope": "universal"
        # }

        return json.loads(response.read())



