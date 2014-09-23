__author__ = 'claygraham'

import json
import uuid

from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from app.models import Issue,Patron,CoinbaseButton,ClaimedIssue,Repository,WatchedRepository,CoinOrder
from app.util.gitpatronhelper import GitpatronHelper

register = template.Library()

@register.filter
def replace(text):

    f = open(settings.STATICFILES_DIRS[0]+'/json/yahoo_fields.json', 'r')
    fields = json.loads(f.read())
    if text in fields['keys']:
        return fields[text]
    else:
        return text

@register.filter
def percentage(value):
    return "{0:.0f}%".format(value * 100)

@register.filter
def btc_cents(value):
    return "{0:g}".format(float(value) / 100000000)


@register.filter
def is_fix_owner(fix_issue,fix_user):

    #has the user proof? see if there is a fix button for this issue
    committer = Patron.objects.get(user=fix_user)
    print committer
    fix_for_user = CoinbaseButton.objects.filter(issue=fix_issue,type="fix",owner=committer)
    return len(fix_for_user) > 0

@register.filter
def is_fixed(fix_issue):
    payments_for_issue = CoinOrder.objects.filter(button__issue=fix_issue,button__type='fix')
    return len(payments_for_issue) > 0

@register.filter
def is_paid(fix_issue):
    payments_for_issue = CoinOrder.objects.filter(button__issue=fix_issue,button__type='fix')
    return len(payments_for_issue) > 0

@register.filter
def paid_order(fix_issue):
    payments_for_issue = CoinOrder.objects.get(button__issue=fix_issue,button__type='fix')
    return payments_for_issue

@register.filter
def fix_order(fix_issue):
    payments_for_issue = CoinOrder.objects.get(button__issue=fix_issue,button__type='fix')
    return payments_for_issue

@register.filter
def payment_amount(fix_issue):
    payment_for_issue = CoinOrder.objects.get(button__issue=fix_issue,button__type='fix')
    return "{0:g}".format(float(payment_for_issue.total_coin_cents) / 100000000)


@register.filter
def is_claimer(claim_issue,claim_user):
    #has the user proof? see if there is a fix button for this issue committer
    patron=Patron.objects.get(user=claim_user)
    claimed = ClaimedIssue.objects.filter(issue=claim_issue,committer=patron)
    return len(claimed) > 0

@register.filter
def is_claimed(claim_issue):
    #has the user proof? see if there is a fix button for this issue committer
    claimed = ClaimedIssue.objects.filter(issue=claim_issue)
    return len(claimed) > 0

@register.filter
def is_claim_closed(claim_issue):
    #has the user proof? see if there is a fix button for this issue committer
    claimed = ClaimedIssue.objects.filter(issue=claim_issue,fixed=True)
    return len(claimed) > 0

@register.filter
def is_repo_owner(issue,repo_user):
    owned_repo = Repository.objects.filter(id=issue.repository.id,owner__user=repo_user)
    return len(owned_repo) > 0

@register.filter
def is_issue_user(issue,user):
    issue_user = Issue.objects.filter(id=issue.id,issue_user__user=user)
    return len(issue_user) > 0

@register.filter
def is_wallet_activated(wallet_user):
    patron=Patron.objects.get(user=wallet_user)
    return (patron.coinbase_access_token is not None and patron.coinbase_access_token != '')

@register.filter
def is_monetized_owner(monetized_issue,fix_user):
    monetize_for_user = CoinbaseButton.objects.filter(issue=monetized_issue,type="patronage",owner__user=fix_user)
    return len(monetize_for_user) > 0

@register.filter
def is_monetized_fixer(monetized_issue,repo_user):
    monetize_for_user = CoinbaseButton.objects.filter(issue=monetized_issue,type="fix",owner__user=repo_user)
    return len(monetize_for_user) > 0

@register.filter
def is_monetized_fix(monetized_issue):
    monetize_for_fix = CoinbaseButton.objects.filter(issue=monetized_issue,type="fix")
    return len(monetize_for_fix) > 0

@register.filter
def is_monetized(issue):
    return len(CoinbaseButton.objects.filter(issue=issue,type='patronage')) > 0

@register.filter
def is_issue_owner(issue,user):
    return len(Issue.objects.filter(repository__owner__user=user, id=issue.id))>0

@register.filter
def is_order_owner(order,user):
    return len(CoinOrder.objects.filter(id=order.id, button__owner__user=user,button__type='fix')) > 0

@register.filter
def is_watched(repository,repo_user):
    watching_for_user = WatchedRepository.objects.filter(watcher__user=repo_user, repository=repository)
    return len(watching_for_user) > 0

@register.filter
def wallet_activation_complete(repo_user):
    return False

@register.filter(name='addcss')
def addcss(field, css):
   return field.as_widget(attrs={"class":css})

@register.filter(name='payment_status_filter')
def payment_status_filter(issue):

    count = 0
    buttons = CoinbaseButton.objects.filter(issue=issue,type='patronage')
    index = len(buttons)

    if index == 1:
        count += 1
        if is_claimed(issue):
            count += 1
            if is_fixed(issue):
                count += 1
            elif is_claim_closed(issue):
                return "none"
    elif index > 1:
        count = 3;

    if count == 0:
        return "none"
    elif count == 1:
        return "monetized"
    elif count == 2:
        return "claimed"
    else:
        return "fixed"

@register.filter
def is_funded(issue):
    patronage_for_issue = CoinOrder.objects.filter(button__issue=issue,button__type='patronage')
    return len(patronage_for_issue) > 0


@register.filter(name='settings_value_filter')
def settings_value_filter(name):
   return getattr(settings, name, "")

class SetVarNode(template.Node):

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        context[self.var_name] = value
        return u""

@register.filter
def wallet_state_filter(wallet_user):
    patron=Patron.objects.get(user=wallet_user)
    index_stage = 1;
    if patron.account_created:
        index_stage += 1

    if patron.wallet_address:
        index_stage += 1

    if (patron.coinbase_access_token is not None and patron.coinbase_access_token != ''):
        index_stage += 1

    if patron.has_donated:
        index_stage += 1

    return index_stage


#--- TAGS  ---------

@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")



@register.simple_tag
def wallet_state(wallet_user):
    patron=Patron.objects.get(user=wallet_user)
    index_stage = 1;
    if patron.account_created:
        index_stage += 1

    if patron.wallet_address:
        index_stage += 1

    if (patron.coinbase_access_token is not None and patron.coinbase_access_token != ''):

        #check if there is an activation button already
        try:
            button = CoinbaseButton.objects.get(external_id=patron.wallet_address,type="activation")
            index_stage += 1

        except ObjectDoesNotExist:

            helper = GitpatronHelper()
            make_resonse = helper.make_button(
                'claytantor',
                0.99,
                "Activation Verification Donation",
                "Make a small donation to verify that your wallet is properly integrated with gitpatron.",
                "activate_callback/?secret=fe5b2912221",
                patron.wallet_address)

            refresh_response = make_resonse['refresh_response']
            button_response = make_resonse['button_response']

            #always update tokens on every oauth call
            patron.coinbase_access_token = button_response['access_token']
            patron.coinbase_refresh_token = button_response['refresh_token']
            patron.save()

            if(button_response['error_code'] == None and patron.wallet_address):

                button_guid = str(uuid.uuid1())

                callback_url = '{0}/{1}'.format(
                    settings.GITPATRON_APP_URL,
                    "activate_callback/?secret=fe5b2912221")

                #create the button
                button_created = CoinbaseButton.objects.create(
                    code=button_response['button']['code'],
                    external_id=patron.wallet_address,
                    button_response=json.dumps(button_response),
                    button_guid=button_guid,
                    callback_url=callback_url,
                    issue=None,
                    type="activation",
                    owner=patron)

                index_stage += 1

    if patron.has_donated:
        index_stage += 1

    return index_stage

@register.simple_tag
def wallet_activation_button_code(wallet_user):
    patron=Patron.objects.get(user=wallet_user)
    try:
        button = CoinbaseButton.objects.get(external_id=patron.wallet_address,type="activation")
        return button.code
    except ObjectDoesNotExist:
        return ''



def set_var(parser, token):
    """
        {% set <var_name>  = <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form:  {% set <var_name>  = <var_value> %}")
    return SetVarNode(parts[1], parts[3])

register.tag('set', set_var)

