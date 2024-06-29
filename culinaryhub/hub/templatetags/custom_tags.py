from django import template
from ..models import *
import random, os
from faker import Faker
register = template.Library()


@register.simple_tag()
def get_cat_list(number=None, is_random=False):
    if is_random and number != None:
        return Category.objects.order_by('?')[:number]
    elif is_random and number == None:
        return Category.objects.order_by('?')
    elif is_random == False and number == None:
        return Category.objects.all()
    elif is_random == False and number != None:
        return Category.objects.all()[:number]


@register.simple_tag(name='lorem_ipsum')
def get_lorem_ipsum():
    f = Faker()
    return f.text(200)


@register.inclusion_tag('hub/inclusion_tags/formset.html')
def render_form(form, header='Заполните форму'):
    return {'form': form,
            'header': header
            }


@register.simple_tag(name='pretty_time')
def pretty_time(time):
    return time.strftime('%M минут')


@register.filter(name='is_favorite')
def is_favorite(recipe, user):
    is_f = False
    for f in user.favorite.all():
        if f.recipe == recipe:
            is_f = True
            break
    return is_f
@register.filter(name="is_subscriber")
def is_subscriber(viewer, author):
    is_sub = False
    for s in author.subscribers.all():
        if s.subscriber == viewer:
            is_sub = True
            return is_sub
    return is_sub
@register.filter(name='slugify_with_underscores')
def slugify_with_underscores(value):
    return value.replace(' ', '_')


@register.simple_tag(name='get_random_avatar')
def get_random_avatar():
    avatar_references = ['/static/hub/images/avatars/avatar{}.PNG'.format(i) for i in range(1, 5)]
    return random.choice(avatar_references)


@register.simple_tag(name='get_item')
def get_item(d: dict, key: str):
    return d.get(key)
