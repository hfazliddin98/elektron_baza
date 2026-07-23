from .models import AmalTarixi


def ip_manzil(request):
    """Foydalanuvchi IP manzili (proksi orqasida ham to'g'ri aniqlanadi)."""
    if request is None:
        return None
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def amal_yoz(user, amal, obyekt='', izoh='', request=None):
    """Amallar tarixiga yozuv qo'shadi.

    Har qanday muhim amaldan keyin chaqiriladi (kirish, tasdiqlash, status
    o'zgartirish va h.k.). Anonim foydalanuvchi uchun `user=None` yoziladi.
    """
    if user is not None and not getattr(user, 'is_authenticated', False):
        user = None
    return AmalTarixi.objects.create(
        user=user,
        amal=amal,
        obyekt=str(obyekt)[:200],
        izoh=izoh,
        ip=ip_manzil(request),
    )
