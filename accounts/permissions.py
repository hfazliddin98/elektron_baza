"""Rol asosidagi ruxsatlar: view'lar uchun dekorator va mixin.

Superuser barcha sahifalarga kira oladi (texnik administrator).
Ruxsatsiz urinishlar amallar tarixiga yoziladi.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import AmalTarixi, User
from .utils import amal_yoz

ADMIN = User.Rol.ADMIN
OPERATOR = User.Rol.OPERATOR
USTA = User.Rol.USTA
XODIM = User.Rol.XODIM
RAHBARIYAT = User.Rol.RAHBARIYAT


def rol_tekshir(user, rollar):
    return bool(user.is_superuser or user.rol in rollar)


def _ruxsatsiz(request, rollar):
    amal_yoz(
        request.user, AmalTarixi.Amal.RUXSATSIZ, obyekt=request.path,
        izoh=f'Kerakli rollar: {", ".join(rollar)}', request=request,
    )
    raise PermissionDenied('Bu sahifaga kirish uchun ruxsatingiz yo\'q.')


def rol_kerak(*rollar):
    """Funksiya-view uchun: @rol_kerak(ADMIN, OPERATOR)"""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if not rol_tekshir(request.user, rollar):
                _ruxsatsiz(request, rollar)
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class RolTalabMixin:
    """Klass-view uchun: `rollar = (ADMIN, OPERATOR)`.

    LoginRequiredMixin bilan birga ishlatiladi.
    """

    rollar = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if self.rollar and not rol_tekshir(request.user, self.rollar):
            _ruxsatsiz(request, self.rollar)
        return super().dispatch(request, *args, **kwargs)
