from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


register = template.Library()

@register.filter(needs_autoescape=True)
def russian_r(text, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    escaped = esc(text)
    return mark_safe(escaped.replace('R', '<span class="russian">R</span>'))
