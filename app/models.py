from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

import re

reply_re = re.compile("^@(\w+)")

#from django.core.management import call_command
#call_command('syncdb', interactive=True)
#call_command('migrate', interactive=True)

class Patron(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=250, unique=False)
    img = models.URLField(default="", verbose_name='Image URL', blank=True, null=True)
    bio = models.TextField( default="", verbose_name='Patron Bio')

    # "login": "claytantor",
    github_login = models.CharField(max_length=250, unique=False)

    #   "id": 407854,
    github_id = models.BigIntegerField(unique=True, blank=True,  null=True)

    #   "avatar_url": "https://avatars.githubusercontent.com/u/407854?",
    github_avatar_url = models.CharField(max_length=250, unique=False)

    #   "gravatar_id": "c88d7ef134a9779657d7d63257b5f725",
    #   "url": "https://api.github.com/users/claytantor",

    #   "html_url": "https://github.com/claytantor",
    #   "followers_url": "https://api.github.com/users/claytantor/followers",
    #   "following_url": "https://api.github.com/users/claytantor/following{/other_user}",
    #   "gists_url": "https://api.github.com/users/claytantor/gists{/gist_id}",
    #   "starred_url": "https://api.github.com/users/claytantor/starred{/owner}{/repo}",
    #   "subscriptions_url": "https://api.github.com/users/claytantor/subscriptions",
    #   "organizations_url": "https://api.github.com/users/claytantor/orgs",
    #   "repos_url": "https://api.github.com/users/claytantor/repos",
    #   "events_url": "https://api.github.com/users/claytantor/events{/privacy}",
    #   "received_events_url": "https://api.github.com/users/claytantor/received_events",

    #   "type": "User",
    github_type = models.CharField(max_length=16, unique=False)

    github_access_token = models.CharField(max_length=64, unique=False)

    coinbase_access_token = models.CharField(max_length=250, unique=False, blank=True,  null=True)

    coinbase_refresh_token = models.CharField(max_length=250, unique=False, blank=True,  null=True)

    coinbase_callback_secret = models.CharField(max_length=128, unique=False, blank=True,  null=True)

    def __unicode__(self):
        return self.github_login


class Repository(models.Model):
    name = models.CharField(max_length=250)
    fullname = models.CharField(max_length=250)
    tagline = models.CharField(max_length=250)
    github_description = models.TextField( default="", verbose_name='Repository Description')
    markdown = models.TextField( default="", verbose_name='Published Repo Info')
    owner = models.ForeignKey('Patron',null=True,blank=True)
    private = models.NullBooleanField(default=False, null=True)

    def __unicode__(self):
        return self.name


class Issue(models.Model):
    
    # # "url": "https://api.github.com/repos/claytantor/grailo/issues/4",
    # name = models.CharField(max_length=250, unique=False)
    github_api_url = models.CharField(max_length=250, unique=False)

    # "html_url": "https://github.com/claytantor/grailo/issues/4",
    github_html_url = models.CharField(max_length=250, unique=False)

    # "id": 8657138,
    github_id = models.BigIntegerField(unique=True, null=True)
    
    # "number": 4,
    github_issue_no = models.BigIntegerField(unique=False, null=True)
    
    # "title": "Message length check",  
    title = models.CharField(max_length=250, unique=False)

    json_body = models.TextField( default="", verbose_name='Issue JSON')

    description = models.TextField( default="", verbose_name='Issue Description')

    repository = models.ForeignKey('Repository',null=True,blank=True)

    def __unicode__(self):
        return '{0} {1}'.format(self.github_id,self.title)





class Reward(models.Model):
    name = models.CharField(max_length=255, default="", verbose_name='Reward Name')
    amount = models.DecimalField(max_digits=8, decimal_places=2, default="", verbose_name="Minimum Amount")
    desc = models.TextField( default="", verbose_name='Reward Description')
    short_desc = models.CharField(max_length=255, default="", verbose_name='Short Reward Description')
    patron = models.ForeignKey('Patron',null=True,blank=True)
    issue = models.ForeignKey('Issue',null=True,blank=True)
    def __unicode__(self):
        return self.name

class Update(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=255)
    text = models.TextField()
    repository = models.ForeignKey('Repository',null=True,blank=True)
    read_status = models.IntegerField(default=0, null=True)
    def __unicode__(self):
        return self.subject

class Comment(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=255)
    text = models.TextField()
    patron = models.ForeignKey('Patron',null=True,blank=True)
    repository = models.ForeignKey('Repository',null=True,blank=True)
    def __unicode__(self):
        return self.subject

class Question(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=255)
    patron = models.ForeignKey('Patron',null=True,blank=True)
    text = models.TextField()

class CallbackMessage(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    message = models.TextField()
    owner = models.ForeignKey('Patron',null=True,blank=True)
    processed_at = models.DateTimeField(null=True,blank=True)
    is_processed = models.NullBooleanField(default=False)
    def __unicode__(self):
        return 'message {0}'.format(self.id)

# {
#     "order": {
#         "id": "5RTQNACF",
#         "created_at": "2012-12-09T21:23:41-08:00",
#         "status": "completed",
#         "total_btc": {
#             "cents": 100000000,
#             "currency_iso": "BTC"
#         },
#         "total_native": {
#             "cents": 1253,
#             "currency_iso": "USD"
#         },
#         "custom": "order1234",
#         "receive_address": "1NhwPYPgoPwr5hynRAsto5ZgEcw1LzM3My",
#         "button": {
#             "type": "buy_now",
#             "name": "Alpaca Socks",
#             "description": "The ultimate in lightweight footwear",
#             "id": "5d37a3b61914d6d0ad15b5135d80c19f"
#         },
#         "transaction": {
#             "id": "514f18b7a5ea3d630a00000f",
#             "hash": "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
#             "confirmations": 0
#         },
#         "customer": {
#             "email": "coinbase@example.com",
#             "shipping_address": [
#                 "John Smith",
#                 "123 Main St.",
#                 "Springfield, OR 97477",
#                 "United States"
#             ]
#         },
#         "refund_address": "1HcmQZarSgNuGYz4r7ZkjYumiU4PujrNYk"
#     }
# }
class CoinOrder(models.Model):
     #"id": "5RTQNACF",
    external_id = models.CharField(max_length=128)
    status = models.CharField(max_length=36)
    total_coin_cents = models.BigIntegerField(default=0, verbose_name="Order BTC Amount")
    total_coin_currency_iso = models.CharField(max_length=3)
    receive_address = models.CharField(max_length=36)
    refund_address = models.CharField(max_length=36)
    button = models.ForeignKey('CoinbaseButton',null=True,blank=True)
    def __unicode__(self):
        return '{0} order for button {1}'.format(self.id, self.button.code)



#         "customer": {
#             "email": "coinbase@example.com",
#             "shipping_address": [
#                 "John Smith",
#                 "123 Main St.",
#                 "Springfield, OR 97477",
#                 "United States"
#             ]
#         },
class CoinCustomer(models.Model):
    email = models.CharField(max_length=64)
    order = models.ForeignKey(CoinOrder)
    addr_name = models.CharField(max_length=64)
    addr1 = models.CharField(max_length=64)
    addr2 = models.CharField(max_length=64)
    addr_contry = models.CharField(max_length=64)



#         "transaction": {
#             "id": "514f18b7a5ea3d630a00000f",
#             "hash": "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
#             "confirmations": 0
#         },
class CoinTransaction(models.Model):
    external_id =models.CharField(max_length=36)
    hash =models.CharField(max_length=64)
    order = models.ForeignKey(CoinOrder)
    confirmations = models.IntegerField(default=0)


class CoinbaseButton(models.Model):
    code = models.CharField(max_length=64)
    external_id = models.TextField()
    button_response = models.TextField()
    type = models.CharField(max_length=16,null=True,blank=True)
    button_guid = models.CharField(max_length=128,null=True,blank=True)
    issue = models.ForeignKey('Issue',null=True,blank=True)
    owner = models.ForeignKey('Patron',null=True,blank=True)
    callback_url = models.CharField(max_length=256,null=True,blank=True)
    total_coin_cents = models.BigIntegerField(default=0,null=True,blank=True)
    total_coin_currency_iso = models.CharField(max_length=3,null=True,blank=True)
    def __unicode__(self):
        return '{0} for {1} {2}'.format(self.type,self.issue.github_id,self.issue.title)

    def is_owned_by(self, user_test):
        return self.owner.user == user_test



class Patronage(models.Model):
    issue = models.ForeignKey('Issue',null=True,blank=True)
    patron = models.ForeignKey('Patron',null=True,blank=True)
    cents = models.BigIntegerField(default=0, null=True, verbose_name="Patronage Cents")
    coinbase_id =models.CharField(max_length=8)
    receive_address = models.CharField(max_length=128,null=True,blank=True)
    refund_address = models.CharField(max_length=128,null=True,blank=True)
    transaction_id = models.CharField(max_length=128,null=True,blank=True)

class ClaimedIssue(models.Model):
    issue = models.ForeignKey('Issue',null=True,blank=True)
    committer = models.ForeignKey('Patron',null=True,blank=True)
    button = models.ForeignKey('CoinbaseButton',null=True,blank=True)
    fixed = models.NullBooleanField(default=False, null=True)
    github_commit_id = models.CharField(max_length=255,null=True,blank=True)
    committer_type = models.CharField(max_length=16,null=True,blank=True)

    def __unicode__(self):
        return '{0} has claimed {1}'.format(self.committer.user.username,self.issue.title)


# class HasOwner(object):
#     """
#     If a model's objects are potentially "owned" by a user (or multiple users),
#     the model's class should inherit from this class and implement is_owned_by.
#     """
#     def is_owned_by(self, user):
#         """
#         Abstract method for determining if a given user owns a given object.
#         """
#         klass = self.__class__.__name__
#         raise NotImplementedError, "method not overridden for class " + klass
#
#     @classmethod
#     def get_mine(klass, user, *args, **kargs):
#         """
#         Utility function to check for existance and ownership of an object and
#         return it or raise either a 404 or PermissionDenied error.
#         """
#         object = get_object_or_404(klass, *args, **kargs)
#         if not object.is_owned_by(user):
#             raise PermissionDenied
#         return object











