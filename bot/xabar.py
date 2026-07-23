"""Telegram orqali xabar yuborish.

Django'ning oddiy (sinxron) kodidan chaqiriladi — bot jarayoni ishlamayotgan
bo'lsa ham xabarlar yuboriladi, chunki to'g'ridan-to'g'ri Telegram API'ga
murojaat qilinadi. Token sozlanmagan bo'lsa hech narsa yubormaydi va
dasturning ishlashiga xalal bermaydi.
"""

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

API_MANZIL = 'https://api.telegram.org/bot{token}/{metod}'
KUTISH = 5  # soniya


def _sorov(metod, malumot):
    token = getattr(settings, 'BOT_TOKEN', '')
    if not token:
        return None

    manzil = API_MANZIL.format(token=token, metod=metod)
    payload = json.dumps(malumot).encode()
    sorov = urllib.request.Request(
        manzil, data=payload, headers={'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(sorov, timeout=KUTISH) as javob:
            return json.loads(javob.read())
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as xato:
        logger.warning('Telegram xabari yuborilmadi (%s): %s', metod, xato)
        return None


def xabar_yubor(telegram_id, matn, tugmalar=None):
    """Bitta foydalanuvchiga xabar yuboradi. Muvaffaqiyatli bo'lsa True."""
    if not telegram_id:
        return False
    malumot = {'chat_id': telegram_id, 'text': matn, 'parse_mode': 'HTML'}
    if tugmalar:
        malumot['reply_markup'] = {'inline_keyboard': tugmalar}
    javob = _sorov('sendMessage', malumot)
    return bool(javob and javob.get('ok'))


def xodimga(xodim, matn, tugmalar=None):
    return xabar_yubor(getattr(xodim, 'telegram_id', None), matn, tugmalar)


def ustaga(usta, matn, tugmalar=None):
    return xabar_yubor(getattr(usta, 'telegram_id', None), matn, tugmalar)


def ustalarga(matn, tashqari=None):
    """Barcha faol ustalarga (Telegram'ga ulanganlariga) xabar yuboradi."""
    from accounts.models import Usta

    qs = Usta.objects.filter(faol=True, telegram_id__isnull=False)
    if tashqari is not None:
        qs = qs.exclude(pk=tashqari.pk)
    return sum(1 for usta in qs if ustaga(usta, matn))


def adminlarga(matn):
    """Operator/admin guruhiga xabar (BOT_ADMIN_CHAT sozlangan bo'lsa)."""
    chat = getattr(settings, 'BOT_ADMIN_CHAT', '')
    if not chat:
        return False
    return xabar_yubor(chat, matn)
