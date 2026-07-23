"""Hisobot ma'lumotlarini hisoblash.

Bir joyda hisoblanadi — HTML sahifa, Excel va PDF ayni shu ma'lumotdan
foydalanadi, shuning uchun raqamlar hech qachon bir-biridan farq qilmaydi.
"""

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from django.db.models import (
    Avg, Count, DurationField, ExpressionWrapper, F, Q, Sum,
)
from django.db.models.functions import TruncMonth
from django.utils import timezone

from accounts.models import Usta
from devices.models import Bolim, Qurilma, Xodim
from repairs.models import TamirYozuvi

Holat = TamirYozuvi.Holat
Turi = TamirYozuvi.Turi
Tasdiq = TamirYozuvi.Tasdiq

OYLAR = [
    'yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun',
    'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr',
]


@dataclass
class Davr:
    boshlanish: date
    tugash: date

    @property
    def nomi(self):
        if self.boshlanish.day == 1 and self.tugash.day == monthrange(
                self.tugash.year, self.tugash.month)[1]:
            if self.boshlanish.month == 1 and self.tugash.month == 12 \
                    and self.boshlanish.year == self.tugash.year:
                return f'{self.boshlanish.year}-yil'
            if (self.boshlanish.year, self.boshlanish.month) == (self.tugash.year, self.tugash.month):
                return f'{self.boshlanish.year}-yil {OYLAR[self.boshlanish.month - 1]}'
        return f'{self.boshlanish:%d.%m.%Y} — {self.tugash:%d.%m.%Y}'

    @property
    def oraliq(self):
        """Vaqt mintaqasini hisobga olgan (boshlanish, tugash) juftligi."""
        tz = timezone.get_current_timezone()
        return (
            timezone.make_aware(datetime.combine(self.boshlanish, time.min), tz),
            timezone.make_aware(datetime.combine(self.tugash, time.max), tz),
        )


def joriy_oy():
    bugun = timezone.localdate()
    return Davr(bugun.replace(day=1), bugun)


def davr_aniqla(dan, gacha):
    """GET parametrlaridan davr yasaydi; noto'g'ri bo'lsa joriy oy."""
    if dan and gacha and dan <= gacha:
        return Davr(dan, gacha)
    return joriy_oy()


def _kun(muddat):
    """timedelta → kun (1 xonali), bo'sh bo'lsa None."""
    if muddat is None:
        return None
    return round(muddat.total_seconds() / 86400, 1)


def _ortacha_muddat(qs, boshi, oxiri):
    natija = qs.filter(**{f'{boshi}__isnull': False, f'{oxiri}__isnull': False}).aggregate(
        o=Avg(ExpressionWrapper(F(oxiri) - F(boshi), output_field=DurationField()))
    )['o']
    return _kun(natija)


def yig(davr):
    """Davr uchun barcha hisobot bo'limlarini hisoblaydi."""
    boshlanish, tugash = davr.oraliq

    # Davrda kelib tushgan murojaatlar (rad etilganlar ham hisobda)
    kelganlar = TamirYozuvi.objects.filter(qabul_sana__range=(boshlanish, tugash))
    usta_kelganlar = kelganlar.filter(turi=Turi.USTA)
    # Davrda topshirilgan (tugatilgan) ta'mirlar
    tugatilganlar = TamirYozuvi.objects.filter(
        holat=Holat.TOPSHIRILDI, topshirilgan_sana__range=(boshlanish, tugash),
    )

    umumiy = {
        'kelgan': usta_kelganlar.count(),
        'tugatilgan': tugatilganlar.count(),
        'rad_etilgan': usta_kelganlar.filter(holat=Holat.RAD).count(),
        'jarayonda': TamirYozuvi.objects.jarayondagi().count(),
        'ozi_tamir': kelganlar.filter(turi=Turi.OZI, tasdiq_holati=Tasdiq.TASDIQLANDI).count(),
        'ozi_tamir_rad': kelganlar.filter(turi=Turi.OZI, tasdiq_holati=Tasdiq.RAD).count(),
        'ortacha_muddat': _ortacha_muddat(tugatilganlar, 'qabul_sana', 'topshirilgan_sana'),
        'ortacha_baho': tugatilganlar.filter(baho__isnull=False).aggregate(o=Avg('baho'))['o'],
        'baholanmagan': tugatilganlar.filter(baho__isnull=True).count(),
        'xarajat': (kelganlar.hisobga_kiradi().aggregate(s=Sum('xarajat'))['s'] or 0),
        'shoshilinch': usta_kelganlar.filter(
            muhimlik=TamirYozuvi.Muhimlik.SHOSHILINCH).count(),
        'qayta_tamir': usta_kelganlar.filter(qayta_tamir__isnull=False).count(),
        'kechikkan': TamirYozuvi.objects.kechikkanlar().count(),
    }

    bosqichlar = [
        ('Qabuldan navbatgacha (operator)', _ortacha_muddat(
            tugatilganlar, 'qabul_sana', 'navbatga_tushgan')),
        ('Navbatda kutish', _ortacha_muddat(
            tugatilganlar, 'navbatga_tushgan', 'boshlangan_sana')),
        ("Ta'mir ishlari", _ortacha_muddat(
            tugatilganlar, 'boshlangan_sana', 'tugagan_sana')),
        ('Tayyordan topshirishgacha', _ortacha_muddat(
            tugatilganlar, 'tugagan_sana', 'topshirilgan_sana')),
    ]

    ustalar = list(
        Usta.objects.annotate(
            tamirlar_soni=Count('tamirlar', filter=Q(
                tamirlar__holat=Holat.TOPSHIRILDI,
                tamirlar__topshirilgan_sana__range=(boshlanish, tugash)), distinct=True),
            reyting=Avg('tamirlar__baho', filter=Q(
                tamirlar__topshirilgan_sana__range=(boshlanish, tugash))),
            qayta_soni=Count('tamirlar__qayta_tamirlar', distinct=True),
            soralgan_soni=Count('soralgan_tamirlar', filter=Q(
                soralgan_tamirlar__qabul_sana__range=(boshlanish, tugash)), distinct=True),
            aktiv=Count('tamirlar', filter=Q(
                tamirlar__holat__in=[Holat.TASHXIS, Holat.TAMIRDA]), distinct=True),
        ).order_by('-tamirlar_soni', 'fio')
    )
    for usta in ustalar:
        usta.qayta_foiz = (
            round(usta.qayta_soni * 100 / usta.tamirlar_soni, 1) if usta.tamirlar_soni else 0
        )

    xodimlar = list(
        Xodim.objects.annotate(
            murojaat_soni=Count('tamirlar', filter=Q(
                tamirlar__turi=Turi.USTA,
                tamirlar__qabul_sana__range=(boshlanish, tugash)), distinct=True),
            ozi_soni=Count('tamirlar', filter=Q(
                tamirlar__turi=Turi.OZI, tamirlar__tasdiq_holati=Tasdiq.TASDIQLANDI,
                tamirlar__qabul_sana__range=(boshlanish, tugash)), distinct=True),
        ).filter(Q(murojaat_soni__gt=0) | Q(ozi_soni__gt=0))
        .select_related('bolim').order_by('-murojaat_soni', 'fio')
    )

    bolimlar = list(
        Bolim.objects.annotate(
            murojaat_soni=Count('qurilmalar__tamirlar', filter=Q(
                qurilmalar__tamirlar__qabul_sana__range=(boshlanish, tugash)), distinct=True),
            qurilmalar_soni=Count('qurilmalar', distinct=True),
        ).order_by('-murojaat_soni', 'nomi')
    )

    qurilmalar = list(
        Qurilma.objects.annotate(
            tamir_soni=Count('tamirlar', filter=Q(
                tamirlar__qabul_sana__range=(boshlanish, tugash)), distinct=True),
            xarajat=Sum('tamirlar__xarajat', filter=Q(
                tamirlar__qabul_sana__range=(boshlanish, tugash))),
        ).filter(tamir_soni__gt=0).select_related('bolim').order_by('-tamir_soni')[:15]
    )

    manbalar = [
        {'nomi': nom, 'soni': usta_kelganlar.filter(manba=kod).count()}
        for kod, nom in TamirYozuvi.Manba.choices
    ]

    oylar = _oylik_dinamika()

    return {
        'davr': davr,
        'umumiy': umumiy,
        'bosqichlar': bosqichlar,
        'ustalar': ustalar,
        'xodimlar': xodimlar,
        'bolimlar': bolimlar,
        'qurilmalar': qurilmalar,
        'manbalar': manbalar,
        'oylar': oylar,
        'kechikkanlar': list(
            TamirYozuvi.objects.kechikkanlar()
            .select_related('qurilma', 'usta').order_by('holat_sana')[:20]
        ),
    }


def _oylik_dinamika(oylar_soni=12):
    """Oxirgi 12 oy bo'yicha murojaat va tugatish dinamikasi (diagramma uchun)."""
    bugun = timezone.localdate()
    boshi = (bugun.replace(day=1) - timedelta(days=31 * (oylar_soni - 1))).replace(day=1)
    tz = timezone.get_current_timezone()
    boshi_vaqt = timezone.make_aware(datetime.combine(boshi, time.min), tz)

    kelgan = dict(
        TamirYozuvi.objects.filter(qabul_sana__gte=boshi_vaqt, turi=Turi.USTA)
        .annotate(oy=TruncMonth('qabul_sana')).values_list('oy')
        .annotate(soni=Count('id')).values_list('oy', 'soni')
    )
    tugatilgan = dict(
        TamirYozuvi.objects.filter(topshirilgan_sana__gte=boshi_vaqt)
        .annotate(oy=TruncMonth('topshirilgan_sana')).values_list('oy')
        .annotate(soni=Count('id')).values_list('oy', 'soni')
    )

    def kalit_qidir(xarita, yil, oy):
        for kalit, qiymat in xarita.items():
            sana = timezone.localtime(kalit) if timezone.is_aware(kalit) else kalit
            if sana.year == yil and sana.month == oy:
                return qiymat
        return 0

    natija = []
    yil, oy = boshi.year, boshi.month
    for _ in range(oylar_soni):
        natija.append({
            'nomi': f'{OYLAR[oy - 1][:3]} {str(yil)[2:]}',
            'kelgan': kalit_qidir(kelgan, yil, oy),
            'tugatilgan': kalit_qidir(tugatilgan, yil, oy),
        })
        oy += 1
        if oy > 12:
            oy, yil = 1, yil + 1
    return natija
