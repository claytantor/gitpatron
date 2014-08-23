__author__ = 'claygraham'
import json
from django import template
from django.conf import settings

from app.models import Issue,Patron,CoinbaseButton,ClaimedIssue,Repository,WatchedRepository,CoinOrder


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

    fix_for_issue = ClaimedIssue.objects.filter(issue=fix_issue,fixed=True)
    return len(fix_for_issue) > 0

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
    return len(CoinbaseButton.objects.filter(issue=issue,type='patronage'))>0

@register.filter
def is_issue_owner(issue,user):
    return len(Issue.objects.filter(repository__owner__user=user, id=issue.id))>0

@register.filter
def is_order_owner(order,user):
    return len(CoinOrder.objects.filter(id=order.id, button__owner__user=user,button__type='fix'))>0

@register.filter
def is_watched(repository,repo_user):
    watching_for_user = WatchedRepository.objects.filter(watcher__user=repo_user, repository=repository)
    return len(watching_for_user) > 0


@register.filter(name='addcss')
def addcss(field, css):
   return field.as_widget(attrs={"class":css})

@register.simple_tag
def settings_value(name):
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

def set_var(parser, token):
    """
        {% set <var_name>  = <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form:  {% set <var_name>  = <var_value> %}")
    return SetVarNode(parts[1], parts[3])

register.tag('set', set_var)

