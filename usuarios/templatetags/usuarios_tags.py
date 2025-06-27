from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def split(value, arg):
    """
    Divide uma string pelo argumento fornecido.
    Exemplo: {{ value|split:',' }}
    """
    return value.split(arg)
