import json
import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from app.models import Patron, CallbackMessage, CoinbaseButton, \
    Issue, Repository, ClaimedIssue, CoinOrder

class Command(BaseCommand):

    def handle(self, *args, **options):
        messages = CallbackMessage.objects.filter(is_processed=False)
        for message in messages:
            print message.message

            # {
            #     "order": {
            #         "id": "67FUOTZY",
            #         "created_at": "2014-05-26T20:35:47-07:00",
            #         "status": "completed",
            #         "event": {
            #             "type": "completed"
            #         },
            #         "total_btc": {
            #             "cents": 170200,
            #             "currency_iso": "BTC"
            #         },
            #         "total_native": {
            #             "cents": 100,
            #             "currency_iso": "USD"
            #         },
            #         "total_payout": {
            #             "cents": 0,
            #             "currency_iso": "USD"
            #         },
            #         "custom": "https://api.github.com/repos/claytantor/grailo/issues/1",
            #         "receive_address": "1JeduwWzd8fxQBaJ4umKdmttgXnJ6UpPtB",
            #         "button": {
            #             "type": "buy_now",
            #             "name": "8656458 Async all client side decryption.",
            #             "description": "Async all client side decryption.",
            #             "id": "cadb251e212ce71a16022f5854b9566d"
            #         },
            #         "refund_address": "1LDRmekErfo7VtDyP22W1z5bR5vQR6avY3",
            #         "transaction": {
            #             "id": "5384082423761e82f9000008",
            #             "hash": null,
            #             "confirmations": 0
            #         }
            #     }
            # }

            callback_message = json.loads(message.message)
            order_message = callback_message['order']

            #find the button related to this order
            order_button = CoinbaseButton.objects.get(code=order_message['button']['id'])

            order = CoinOrder.objects.create(
                # external_id = models.CharField(max_length=12)
                external_id = order_message['id'],
                # status = models.CharField(max_length=12)
                status = order_message['status'],
                # total_coin_cents = models.DecimalField(max_digits=8, decimal_places=8, default="", verbose_name="Order BTC Amount")
                total_coin_cents = order_message['total_btc']['cents'],
                # total_coin_currency_iso = models.CharField(max_length=3)
                total_coin_currency_iso = order_message['total_btc']['currency_iso'],
                # receive_address = models.CharField(max_length=36)
                receive_address = order_message['receive_address'],
                # refund_address = models.CharField(max_length=36)
                refund_address = order_message['refund_address'],
                button = order_button
            )

            message.is_processed = True
            message.processed_at = timezone.now()
            message.owner = order_button.owner
            message.save()
