
from django import template

register = template.Library()

CENSORED_WORDS = ['редиска', 'нецензурное', 'слово']  # список слов, которые нужно цензурировать


@register.filter(name='censor')
def censor(value):
    if not isinstance(value, str):
        raise ValueError("Фильтр censor может применяться только к строкам.")

    for word in CENSORED_WORDS:
        value = value.replace(word, word[0] + '*' * (len(word) - 1))
    return value
