from django import template

register = template.Library()

def get_from_dict(dictionary, key):
    return dictionary.get(key)

register.filter('get_from_dict', get_from_dict)
