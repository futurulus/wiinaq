# -*- coding: utf-8 -*-
import re
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


register = template.Library()


def replace_comment_newlines(escaped):
    return escaped.replace('\n', '</p><p class="comments">')


def replace_russian_r_nocaps(escaped):
    return (escaped.replace('ř', 'ʀ')
                   .replace('Ř', 'Ʀ'))


def replace_russian_r(escaped):
    escaped = replace_russian_r_nocaps(escaped)
    return escaped[0:1] + escaped[1:].replace('R', 'ʀ')


def replace_superscript(escaped):
    return re.sub(r'\\([a-z])', r'<sup>\1</sup>', escaped)


def replace_double(escaped):
    return re.sub(r'(r|g)\1', r'<u>\1</u>', escaped)


def replace_e_noun_stem(escaped):
    return re.sub(r'[AE]$', r'e', escaped)


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
def russian_r_nocaps(text, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    escaped = esc(text)
    return mark_safe(replace_russian_r_nocaps(escaped))


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


def format_tildes(escaped):
    return re.sub(r'~([^~]+)~', r'<span class="tildes">\1</span>', escaped)


def format_backticks(escaped):
    return re.sub(r'`([^`]+)`', r'<span class="backticks">\1</span>', escaped)


def format_superscripts(escaped):
    grouped = re.sub(r'\$\{([^}]+)\}', r'<sup>\1</sup>', escaped)
    return re.sub(r'\$(\d+|.)', r'<sup>\1</sup>', grouped)


def format_subscripts(escaped):
    grouped = re.sub(r'(?<!&)#\{([^}]+)\}', r'<sub>\1</sub>', escaped)
    return re.sub(r'(?<!&)#(\d+|.)', r'<sub>\1</sub>', grouped)


@register.filter(needs_autoescape=True)
def markup(text, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    result = esc(text)
    for transform in [format_tildes,
                      format_backticks,
                      format_superscripts,
                      format_subscripts]:
        result = transform(result)
    return mark_safe(result)
