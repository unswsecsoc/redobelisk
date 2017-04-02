from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect


def check_authenticated(function):
    def wrap(request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                return function(request, *args, **kwargs)
            else:
                raise
        except:
            return HttpResponseRedirect("/login")
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap
