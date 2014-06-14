__author__ = 'claygraham'
import json
from django import template
from django.conf import settings

from app.models import Issue,Patron,CoinbaseButton,ClaimedIssue,Repository


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
def is_monetized_owner(monetized_issue,repo_user):
    monetize_for_user = CoinbaseButton.objects.filter(issue=monetized_issue,type="patronage",owner__user=repo_user)
    return len(monetize_for_user) > 0

@register.filter
def is_monetized_fixer(monetized_issue,repo_user):
    monetize_for_user = CoinbaseButton.objects.filter(issue=monetized_issue,type="fix",owner__user=repo_user)
    return len(monetize_for_user) > 0

@register.filter
def is_monetized(issue):
    return len(CoinbaseButton.objects.filter(issue=issue,type='patronage'))>0




@register.filter(name='addcss')
def addcss(field, css):
   return field.as_widget(attrs={"class":css})



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

