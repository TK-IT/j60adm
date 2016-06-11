from django import template
import json as simplejson

register = template.Library()

@register.filter
def json(value):
    return simplejson.dumps(value)
