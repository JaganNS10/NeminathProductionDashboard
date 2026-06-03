
from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    """Allow dict lookup by variable key in Django templates."""
    return d.get(key)
