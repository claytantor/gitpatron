from django.conf import settings
from app.models import Patron
from app.util.coinbasev1 import CoinbaseV1


class GitpatronHelper():

    def refresh_user_token(
            self,
            username):
        patron = Patron.objects.get(user__username=username)

        coinbase_client = CoinbaseV1()

        refresh_response = coinbase_client.refresh_token(
            patron.coinbase_refresh_token,
            settings.COINBASE_OAUTH_CLIENT_ID,
            settings.COINBASE_OAUTH_CLIENT_SECRET)

        patron.coinbase_access_token = refresh_response['access_token']
        patron.coinbase_refresh_token = refresh_response['refresh_token']
        patron.save()

        return {'access_token':refresh_response['access_token'],'refresh_token':refresh_response['refresh_token']}

    def make_button(
            self,
            username,
            amount,
            name,
            description,
            callback_url,
            custom):

        patron = Patron.objects.get(user__username=username)

        callback_url = '{0}/{1}'.format(
            settings.GITPATRON_APP_URL,
            callback_url)

        coinbase_client = CoinbaseV1()

        # patron_username,
        #             coinbase_callback_secret,
        #             name,
        #             amount,
        #             description,
        #             refresh_token
        make_resonse = coinbase_client.make_button(
            amount,
            name,
            description,
            patron.coinbase_refresh_token,
            callback_url,
            custom
        )

        refresh_response = make_resonse['refresh_response']

        patron.coinbase_access_token = refresh_response['access_token']
        patron.coinbase_refresh_token = refresh_response['refresh_token']
        patron.save()

        return make_resonse

