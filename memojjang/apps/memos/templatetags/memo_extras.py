from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """딕셔너리에서 키로 값을 가져오는 필터"""
    if dictionary and key:
        return dictionary.get(key, 0)
    return 0