"""Bot uchun bazaga murojaatlar.

Bu yerdagi funksiyalar oddiy (sinxron) Django ORM kodidir — bot ularni
`sync_to_async` orqali chaqiradi. Shu sababli ularni testda ham to'g'ridan-to'g'ri
sinab ko'rish mumkin.
"""

import re

from accounts.models import Usta
from devices.models import Qurilma, Xodim
from repairs import xabarnomalar
from repairs.models import TamirYozuvi


def telefon_tozala(raqam):
    """Telefon raqamdan faqat oxirgi 9 ta raqamni oladi (+998 91 234 56 78 → 912345678)."""
    raqamlar = re.sub(r'\D', '', raqam or '')
    return raqamlar[-9:] if len(raqamlar) >= 9 else raqamlar


def foydalanuvchini_bogla(telegram_id, telefon):
    """Telefon raqami bo'yicha xodim yoki ustani topib, telegram_id ni saqlaydi.

    Qaytaradi: ('xodim'|'usta'|None, obyekt|None)
    """
    oxirgi = telefon_tozala(telefon)
    if len(oxirgi) < 9:
        return None, None

    for tur, model in (('xodim', Xodim), ('usta', Usta)):
        for obyekt in model.objects.exclude(telefon=''):
            if telefon_tozala(obyekt.telefon) != oxirgi:
                continue
            # Bitta Telegram hisobi faqat bitta profilga bog'lanadi:
            # eski bog'lanishlar (ikkala jadvalda ham) uziladi.
            for boshqa_model in (Xodim, Usta):
                boshqa_model.objects.filter(telegram_id=telegram_id).exclude(
                    pk=obyekt.pk if boshqa_model is model else None,
                ).update(telegram_id=None)
            obyekt.telegram_id = telegram_id
            obyekt.save(update_fields=['telegram_id'])
            return tur, obyekt
    return None, None


def xodim_top(telegram_id):
    return Xodim.objects.filter(telegram_id=telegram_id).select_related('bolim').first()


def usta_top(telegram_id):
    return Usta.objects.filter(telegram_id=telegram_id).first()


def xodim_qurilmalari(xodim, qidiruv=''):
    qs = Qurilma.objects.filter(bolim=xodim.bolim).exclude(holati=Qurilma.Holat.YAROQSIZ)
    if qidiruv:
        qs = qs.filter(inventar_raqami__icontains=qidiruv)
    return list(qs.order_by('inventar_raqami')[:20])


def qurilma_top(pk):
    return Qurilma.objects.filter(pk=pk).first()


def faol_ustalar():
    return list(Usta.objects.filter(faol=True).order_by('fio'))


def murojaat_yarat(xodim, qurilma_id, matn, shoshilinch=False, usta_id=None):
    tamir = TamirYozuvi.objects.create(
        qurilma_id=qurilma_id,
        xodim=xodim,
        manba=TamirYozuvi.Manba.BOT,
        muhimlik=(TamirYozuvi.Muhimlik.SHOSHILINCH if shoshilinch
                  else TamirYozuvi.Muhimlik.ODDIY),
        muammo_tavsifi=matn,
        tanlangan_usta_id=usta_id,
    )
    xabarnomalar.yangi_murojaat(tamir)
    return tamir


def mening_murojaatlarim(xodim, soni=10):
    return list(
        TamirYozuvi.objects.filter(xodim=xodim)
        .select_related('qurilma', 'usta').order_by('-qabul_sana')[:soni]
    )


def usta_ishlari(usta):
    return list(
        TamirYozuvi.objects.filter(
            usta=usta, holat__in=[TamirYozuvi.Holat.TASHXIS, TamirYozuvi.Holat.TAMIRDA],
        ).select_related('qurilma', 'xodim').order_by('holat_sana')
    )


def usta_navbati(usta):
    soralgan = list(
        TamirYozuvi.objects.ustaga_soralgan(usta)
        .select_related('qurilma', 'xodim').navbat_tartibi()
    )
    erkin = list(
        TamirYozuvi.objects.erkin_navbat()
        .select_related('qurilma', 'xodim').navbat_tartibi()[:TamirYozuvi.NAVBAT_HAJMI]
    )
    return soralgan, erkin


def baho_qoy(telegram_id, tamir_id, baho):
    """Bot orqali baho qo'yadi. (muvaffaqiyat, xabar) qaytaradi."""
    xodim = xodim_top(telegram_id)
    if xodim is None:
        return False, "Hisobingiz tizimga ulanmagan. /start buyrug'ini yuboring."

    tamir = TamirYozuvi.objects.filter(pk=tamir_id, xodim=xodim).first()
    if tamir is None:
        return False, 'Bu ta\'mir sizga tegishli emas.'
    if not tamir.baho_kutilmoqda:
        return False, 'Bu ta\'mirni hozir baholab bo\'lmaydi.'

    from django.utils import timezone

    tamir.baho = baho
    tamir.baho_sana = timezone.now()
    tamir.save(update_fields=['baho', 'baho_sana'])
    if baho <= 2:
        xabarnomalar.past_baho(tamir)
    return True, f'Bahoyingiz qabul qilindi: {baho}/5. Rahmat!'
