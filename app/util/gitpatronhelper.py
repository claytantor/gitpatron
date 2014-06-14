import urllib2
import json
from django.conf import settings
import hashlib
import hmac
import time

from app.models import Patron, CallbackMessage, CoinbaseButton, \
    Issue, Repository, ClaimedIssue, CoinOrder

from app.util.coinbasev1 import CoinbaseV1

class GitpatronHelper():

    def refresh_user_token(
            self,
            username):
        patron = Patron.objects.get(user__username=username)

        coinbase_client = CoinbaseV1()

        refresh_response = coinbase_client.refresh_token(
            patron.coinbase_access_token,
            patron.coinbase_refresh_token,
            settings.COINBASE_OAUTH_CLIENT_ID,
            settings.COINBASE_OAUTH_CLIENT_SECRET)

        patron.coinbase_access_token = refresh_response['access_token']
        patron.coinbase_refresh_token = refresh_response['refresh_token']
        patron.save()

        return {'access_token':refresh_response['access_token'],'refresh_token':refresh_response['refresh_token']}

