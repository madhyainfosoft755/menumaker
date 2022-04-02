from django import template
register=template.Library()

@register.filter(name='first')
def first_letter(value):
    return value[:1].upper()
# register.filter('first',first_letter)
