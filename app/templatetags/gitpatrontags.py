__author__ = 'claygraham'
import json
from django import template
from django.conf import settings


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
