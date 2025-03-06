from django import template

register = template.Library()

@register.filter(name='mask_card_number')
def mask_card_number(card_number):
    return '**** **** **** ' + card_number[-4:]
