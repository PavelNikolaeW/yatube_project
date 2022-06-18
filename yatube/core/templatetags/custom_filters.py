from django.template import Library
from django.template.defaultfilters import stringfilter
# В template.Library зарегистрированы все встроенные теги и фильтры шаблонов;
# добавляем к ним и наш фильтр.
register = Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
@stringfilter
def print_n_chars(string, n=30):
    return string[0: n]


@register.filter
@stringfilter
def activate_if_matched(arg1, arg2):
    if arg1 == arg2:
        return "active"
    return ""


@register.filter
@stringfilter
def concat(arg1, arg2):
    return arg1 + arg2


@register.filter
def print_dir(src):
    return dir(src)


cash_strstr = {}


@register.filter
def strstr(str1, str2):
    cash_result = cash_strstr.get(str1)
    if cash_result:
        return cash_result
    cash_strstr[str1] = str2 in str1
    return cash_strstr[str1]
