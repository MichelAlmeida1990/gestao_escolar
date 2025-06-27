from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Retorna o valor de uma chave específica de um dicionário.
    Uso: {{ dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    """
    Multiplica um valor por um argumento.
    Uso: {{ value|multiply:arg }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
