from django import template

register = template.Library()

@register.filter
def money(value):
    try:
        value = float(value)
        return f"{value:,.2f}"
    except:
        return value
