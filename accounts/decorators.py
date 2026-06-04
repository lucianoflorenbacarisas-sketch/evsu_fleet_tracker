from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps


def role_required(allowed_roles=[]):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:

                return redirect('/accounts/login/')

            # SUPERUSER ALWAYS ALLOWED
            if request.user.is_superuser:

                return view_func(
                    request,
                    *args,
                    **kwargs
                )

            # ROLE CHECK
            if request.user.role in allowed_roles:

                return view_func(
                    request,
                    *args,
                    **kwargs
                )

            # BLOCK ACCESS
            return HttpResponseForbidden(
                "ACCESS DENIED"
            )

        return wrapper

    return decorator