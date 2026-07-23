from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import AmalTarixi
from .utils import amal_yoz


@receiver(user_logged_in)
def kirish_yoz(sender, request, user, **kwargs):
    amal_yoz(user, AmalTarixi.Amal.KIRISH, request=request)


@receiver(user_logged_out)
def chiqish_yoz(sender, request, user, **kwargs):
    if user is not None:
        amal_yoz(user, AmalTarixi.Amal.CHIQISH, request=request)


@receiver(user_login_failed)
def kirish_xato_yoz(sender, credentials, request=None, **kwargs):
    amal_yoz(
        None, AmalTarixi.Amal.KIRISH_XATO,
        obyekt=credentials.get('username', ''), request=request,
    )
