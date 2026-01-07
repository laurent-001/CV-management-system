from django import template

register = template.Library()

@register.filter
def split(value, key):
    """
        Returns the value turned into a list.
        Returns an empty list if the value is None or an empty string.
    """
    if value is None or value == "":
        return []
    return value.split(key)
