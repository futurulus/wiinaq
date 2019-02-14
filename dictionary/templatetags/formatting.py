import re
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


register = template.Library()


def replace_comment_newlines(escaped):
    return escaped.replace('\n', '</p><p class="comments">')


def replace_russian_r(escaped):
    return escaped.replace('R', '<span class="russian">R</span>')


def replace_superscript(escaped):
    return re.sub(r'\\([a-z])', r'<sup>\1</sup>', escaped)


def replace_double(escaped):
    return re.sub(r'(r|g)\1', r'<u>\1</u>', escaped)


def replace_e_noun_stem(escaped):
    return re.sub(r'A', r'e', escaped)


@register.filter(needs_autoescape=True)
def comment_newlines(text, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    escaped = esc(text)
    return mark_safe(replace_comment_newlines(escaped))


@register.filter(needs_autoescape=True)
def russian_r(text, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    escaped = esc(text)
    return mark_safe(replace_russian_r(escaped))


@register.filter(needs_autoescape=True)
def root(text, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    result = esc(text)
    for transform in [replace_russian_r,
                      replace_superscript,
                      replace_double,
                      replace_e_noun_stem]:
        result = transform(result)
    return mark_safe(result)
