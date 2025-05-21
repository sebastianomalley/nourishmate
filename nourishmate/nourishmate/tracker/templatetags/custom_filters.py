"""
Template filters for accessing dictionary items and computing percentages.
"""

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Return the value for `key` in the given dictionary, or 0 if the key is missing.
    """
    try:
        return dictionary.get(key, 0)
    except AttributeError:
        return 0

@register.filter
def percent(value, total):
    """
    Compute (value/total) as a rounded percentage.

    Returns:
        int: The percentage (0–100) of `value` over `total`, rounded to the nearest integer.
             Returns 0 if `total` is zero, or if inputs aren’t valid numbers.
    """
    try:
        value = float(value)
        total = float(total)
        return round((value / total) * 100)
    except (ZeroDivisionError, TypeError, ValueError):
        return 0
