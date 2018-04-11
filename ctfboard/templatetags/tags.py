from django import template

register = template.Library()
from ctfboard.models import CTF

@register.simple_tag
def get_ctfs(request):
    ctfs = CTF.objects.all()
    return ctfs
