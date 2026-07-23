from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import AmalTarixi
from accounts.permissions import ADMIN, OPERATOR, USTA, XODIM, rol_kerak
from accounts.utils import amal_yoz

from . import xabarnomalar
from .forms import (
    BahoForm, BiriktirishForm, MurojaatForm, OperatorMurojaatForm, OziTamirForm,
    RadForm, TasdiqForm, YakunlashForm,
)
from .models import TamirYozuvi

Holat = TamirYozuvi.Holat
Tasdiq = TamirYozuvi.Tasdiq


# --- Yordamchilar ---

def _xodim_profili(request):
    xodim = request.user.xodim_profili
    if xodim is None:
        raise PermissionDenied('Hisobingiz xodim yozuvi bilan bog\'lanmagan.')
    return xodim


def _usta_profili(request):
    usta = request.user.usta_profili
    if usta is None:
        raise PermissionDenied('Hisobingiz usta yozuvi bilan bog\'lanmagan.')
    return usta


def _tamir_ol(request, pk):
    """Ta'mir yozuvini oladi; xodim faqat o'z murojaatini ko'ra oladi."""
    tamir = get_object_or_404(
        TamirYozuvi.objects.select_related('qurilma', 'qurilma__bolim', 'xodim',
                                           'usta', 'tanlangan_usta'),
        pk=pk,
    )
    if request.user.is_xodim and tamir.xodim_id != _xodim_profili(request).pk:
        raise PermissionDenied('Bu murojaat sizga tegishli emas.')
    return tamir


def _mening_ishim(request, tamir):
    usta = request.user.usta_profili
    return bool(usta and tamir.usta_id == usta.pk)


def _batafsil_javob(request, tamir, **formalar):
    kontekst = {
        'tamir': tamir,
        'tarix': tamir.status_tarixi.select_related('ozgartirgan'),
        'mening_ishim': _mening_ishim(request, tamir),
        'rad_form': RadForm(prefix='rad'),
        'biriktirish_form': BiriktirishForm(prefix='bir'),
        'yakunlash_form': YakunlashForm(instance=tamir, prefix='yak'),
        'baho_form': BahoForm(instance=tamir, prefix='baho'),
        'tasdiq_form': TasdiqForm(prefix='tas'),
    }
    kontekst.update(formalar)
    return render(request, 'repairs/tamir_batafsil.html', kontekst)


def _holat_tekshir(request, tamir, kutilgan):
    """Amal to'g'ri holatda bajarilayotganini tekshiradi."""
    if tamir.holat != kutilgan:
        messages.error(
            request,
            f'Bu amalni bajarib bo\'lmaydi: ta\'mir hozir «{tamir.holat_nomi}» holatida.',
        )
        return False
    return True


# --- Ro'yxatlar ---

@rol_kerak(ADMIN, OPERATOR, USTA, XODIM)
def tamir_royxati(request):
    qs = TamirYozuvi.objects.select_related('qurilma', 'xodim', 'usta')
    sarlavha = "Ta'mirlar"

    if request.user.is_xodim:
        qs = qs.filter(xodim=_xodim_profili(request))
        sarlavha = 'Mening murojaatlarim'
    elif request.user.is_usta and request.GET.get('mening'):
        qs = qs.filter(usta=_usta_profili(request))
        sarlavha = "Mening ta'mirlarim"

    q = request.GET.get('q', '').strip()
    holat = request.GET.get('holat', '')
    turi = request.GET.get('turi', '')
    muhimlik = request.GET.get('muhimlik', '')

    if q:
        qs = qs.filter(
            Q(qurilma__inventar_raqami__icontains=q)
            | Q(qurilma__modeli__icontains=q)
            | Q(xodim__fio__icontains=q)
            | Q(muammo_tavsifi__icontains=q)
        )
    if holat:
        qs = qs.filter(holat=holat) if holat != 'kechikkan' else qs.kechikkanlar()
    if turi:
        qs = qs.filter(turi=turi)
    if muhimlik:
        qs = qs.filter(muhimlik=muhimlik)

    parametrlar = request.GET.copy()
    parametrlar.pop('page', None)
    sorov = parametrlar.urlencode()

    return render(request, 'repairs/tamir_royxati.html', {
        'sahifa': Paginator(qs, 25).get_page(request.GET.get('page')),
        'sarlavha': sarlavha,
        'jami': qs.count(),
        'holatlar': Holat.choices,
        'turlar': TamirYozuvi.Turi.choices,
        'muhimliklar': TamirYozuvi.Muhimlik.choices,
        'q': q, 'holat': holat, 'turi': turi, 'muhimlik': muhimlik,
        'sorov': f'&{sorov}' if sorov else '',
    })


@rol_kerak(ADMIN, OPERATOR)
def murojaatlar_navbati(request):
    """Operator uchun: ko'rib chiqilmagan yangi murojaatlar."""
    qs = (TamirYozuvi.objects.filter(holat=Holat.YANGI)
          .select_related('qurilma', 'xodim', 'tanlangan_usta').navbat_tartibi())
    return render(request, 'repairs/murojaatlar_navbati.html', {
        'murojaatlar': qs,
        'kechikkanlar': qs.kechikkanlar().count(),
    })


@rol_kerak(ADMIN, USTA)
def navbat(request):
    """Usta uchun: shaxsan so'ralganlar + umumiy navbatning eng eski 10 tasi."""
    usta = request.user.usta_profili
    soralganlar = []
    if usta:
        soralganlar = (TamirYozuvi.objects.ustaga_soralgan(usta)
                       .select_related('qurilma', 'xodim').navbat_tartibi())

    erkin = (TamirYozuvi.objects.erkin_navbat()
             .select_related('qurilma', 'xodim', 'tanlangan_usta')
             .navbat_tartibi()[:TamirYozuvi.NAVBAT_HAJMI])

    return render(request, 'repairs/navbat.html', {
        'usta': usta,
        'soralganlar': soralganlar,
        'erkin': erkin,
        'navbat_hajmi': TamirYozuvi.NAVBAT_HAJMI,
        'jami_navbatda': TamirYozuvi.objects.navbatdagi().count(),
    })


@rol_kerak(ADMIN)
def tasdiqlash_navbati(request):
    """Admin uchun: «o'zim ta'mirladim» hisobotlari."""
    qs = (TamirYozuvi.objects
          .filter(turi=TamirYozuvi.Turi.OZI, tasdiq_holati=Tasdiq.KUTILMOQDA)
          .select_related('qurilma', 'xodim').order_by('qabul_sana'))
    return render(request, 'repairs/tasdiqlash_navbati.html', {'yozuvlar': qs})


@rol_kerak(ADMIN, OPERATOR, USTA, XODIM)
def tamir_batafsil(request, pk):
    return _batafsil_javob(request, _tamir_ol(request, pk))


# --- Yangi yozuvlar ---

@rol_kerak(XODIM)
def murojaat_yangi(request):
    xodim = _xodim_profili(request)
    boshlangich = {}
    qurilma_id = request.GET.get('qurilma')
    if qurilma_id:
        boshlangich['qurilma'] = qurilma_id

    form = MurojaatForm(request.POST or None, request.FILES or None,
                        xodim=xodim, initial=boshlangich)
    if request.method == 'POST' and form.is_valid():
        tamir = form.save(commit=False)
        tamir.xodim = xodim
        tamir.manba = TamirYozuvi.Manba.SAYT
        tamir._ozgartirgan_user = request.user
        tamir.save()

        amal_yoz(request.user, AmalTarixi.Amal.YARATISH,
                 obyekt=f"Murojaat #{tamir.pk}", request=request)
        xabarnomalar.yangi_murojaat(tamir)
        messages.success(request, 'Murojaatingiz yuborildi. Holatini shu yerdan kuzatib boring.')
        return redirect(tamir)

    return render(request, 'repairs/murojaat_form.html', {'form': form})


@rol_kerak(ADMIN, OPERATOR)
def operator_murojaat(request):
    """Xodim qurilmani o'zi olib kelganda operator ochadigan murojaat."""
    form = OperatorMurojaatForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        tamir = form.save(commit=False)
        tamir.manba = TamirYozuvi.Manba.OPERATOR
        tamir._ozgartirgan_user = request.user
        tamir.save()
        # Operator o'zi ochgan murojaat darhol navbatga tushadi
        tamir.holat_ozgartir(Holat.QABUL, user=request.user)

        amal_yoz(request.user, AmalTarixi.Amal.YARATISH,
                 obyekt=f"Murojaat #{tamir.pk}", request=request)
        xabarnomalar.navbatga_tushdi(tamir)
        messages.success(request, f'Murojaat #{tamir.pk} ochildi va navbatga tushdi.')
        return redirect(tamir)

    return render(request, 'repairs/murojaat_form.html', {'form': form, 'operator': True})


@rol_kerak(XODIM)
def ozi_tamir_yangi(request):
    xodim = _xodim_profili(request)
    form = OziTamirForm(request.POST or None, request.FILES or None, xodim=xodim)
    if request.method == 'POST' and form.is_valid():
        tamir = form.save(commit=False)
        tamir.xodim = xodim
        tamir.turi = TamirYozuvi.Turi.OZI
        tamir.manba = TamirYozuvi.Manba.SAYT
        tamir._ozgartirgan_user = request.user
        tamir.save()

        amal_yoz(request.user, AmalTarixi.Amal.YARATISH,
                 obyekt=f"O'zi ta'mirlagan #{tamir.pk}", request=request)
        xabarnomalar.ozi_tamir_yuborildi(tamir)
        messages.success(
            request,
            'Hisobotingiz yuborildi. Admin tasdiqlagach qurilma tarixiga qo\'shiladi.',
        )
        return redirect(tamir)

    return render(request, 'repairs/ozi_tamir_form.html', {'form': form})


# --- Operator amallari ---

@rol_kerak(ADMIN, OPERATOR)
def murojaat_qabul(request, pk):
    tamir = _tamir_ol(request, pk)
    if request.method != 'POST' or not _holat_tekshir(request, tamir, Holat.YANGI):
        return redirect(tamir)

    tamir.holat_ozgartir(Holat.QABUL, user=request.user)
    amal_yoz(request.user, AmalTarixi.Amal.HOLAT,
             obyekt=f"Ta'mir #{tamir.pk}", izoh='Qabul qilindi', request=request)
    xabarnomalar.qabul_qilindi(tamir)
    xabarnomalar.navbatga_tushdi(tamir)
    messages.success(request, f'Murojaat #{tamir.pk} qabul qilindi va navbatga tushdi.')
    return redirect(tamir)


@rol_kerak(ADMIN, OPERATOR)
def murojaat_rad(request, pk):
    tamir = _tamir_ol(request, pk)
    if request.method != 'POST' or not _holat_tekshir(request, tamir, Holat.YANGI):
        return redirect(tamir)

    form = RadForm(request.POST, prefix='rad')
    if not form.is_valid():
        return _batafsil_javob(request, tamir, rad_form=form, rad_ochiq=True)

    tamir.holat_ozgartir(Holat.RAD, user=request.user,
                         rad_sababi=form.cleaned_data['sabab'])
    amal_yoz(request.user, AmalTarixi.Amal.RAD, obyekt=f"Ta'mir #{tamir.pk}",
             izoh=tamir.rad_sababi, request=request)
    xabarnomalar.rad_etildi(tamir)
    messages.success(request, f'Murojaat #{tamir.pk} rad etildi.')
    return redirect(tamir)


@rol_kerak(ADMIN, OPERATOR)
def usta_biriktirish(request, pk):
    """Shoshilinch ishlarni operator to'g'ridan-to'g'ri ustaga biriktiradi."""
    tamir = _tamir_ol(request, pk)
    if request.method != 'POST' or not _holat_tekshir(request, tamir, Holat.QABUL):
        return redirect(tamir)

    form = BiriktirishForm(request.POST, prefix='bir')
    if not form.is_valid():
        return _batafsil_javob(request, tamir, biriktirish_form=form, biriktirish_ochiq=True)

    tamir.holat_ozgartir(Holat.TASHXIS, user=request.user, usta=form.cleaned_data['usta'])
    amal_yoz(request.user, AmalTarixi.Amal.HOLAT, obyekt=f"Ta'mir #{tamir.pk}",
             izoh=f'Usta biriktirildi: {tamir.usta.fio}', request=request)
    xabarnomalar.ustaga_biriktirildi(tamir)
    messages.success(request, f'{tamir.usta.fio} biriktirildi.')
    return redirect(tamir)


@rol_kerak(ADMIN, OPERATOR)
def topshirish(request, pk):
    tamir = _tamir_ol(request, pk)
    if request.method != 'POST' or not _holat_tekshir(request, tamir, Holat.TAYYOR):
        return redirect(tamir)

    tamir.holat_ozgartir(Holat.TOPSHIRILDI, user=request.user)
    amal_yoz(request.user, AmalTarixi.Amal.HOLAT, obyekt=f"Ta'mir #{tamir.pk}",
             izoh='Xodimga topshirildi', request=request)
    xabarnomalar.topshirildi(tamir)
    messages.success(request, 'Qurilma xodimga topshirildi. Endi xodim baho bera oladi.')
    return redirect(tamir)


# --- Usta amallari ---

@rol_kerak(USTA)
def ishni_olish(request, pk):
    """Usta navbatdan ishni o'ziga oladi."""
    usta = _usta_profili(request)
    if request.method != 'POST':
        return redirect('navbat')

    with transaction.atomic():
        tamir = get_object_or_404(TamirYozuvi.objects.select_for_update(), pk=pk)
        if tamir.usta_id or tamir.holat != Holat.QABUL:
            messages.warning(request, 'Bu ishni boshqa usta olib ulgurdi.')
            return redirect('navbat')

        muddat_otgan = (
            tamir.navbatga_tushgan is None
            or (timezone.now() - tamir.navbatga_tushgan).days >= TamirYozuvi.TANLANGAN_USTA_KUN
        )
        if tamir.tanlangan_usta_id and tamir.tanlangan_usta_id != usta.pk and not muddat_otgan:
            messages.warning(request, 'Bu ish boshqa ustadan so\'ralgan — hozircha unga tegishli.')
            return redirect('navbat')

        tamir.holat_ozgartir(Holat.TASHXIS, user=request.user, usta=usta)

    amal_yoz(request.user, AmalTarixi.Amal.HOLAT, obyekt=f"Ta'mir #{tamir.pk}",
             izoh='Usta ishni o\'ziga oldi', request=request)
    xabarnomalar.ustaga_biriktirildi(tamir)
    messages.success(request, f'Ta\'mir #{tamir.pk} sizga biriktirildi.')
    return redirect(tamir)


@rol_kerak(USTA)
def soralganni_rad(request, pk):
    """Usta o'zidan shaxsan so'ralgan ishni rad etadi — umumiy navbatga tushadi."""
    usta = _usta_profili(request)
    tamir = get_object_or_404(TamirYozuvi, pk=pk)
    if request.method != 'POST':
        return redirect('navbat')

    if tamir.tanlangan_usta_id != usta.pk or tamir.holat != Holat.QABUL:
        messages.error(request, 'Bu ish sizdan so\'ralmagan.')
        return redirect('navbat')

    tamir.tanlangan_usta = None
    tamir.save(update_fields=['tanlangan_usta'])
    amal_yoz(request.user, AmalTarixi.Amal.RAD, obyekt=f"Ta'mir #{tamir.pk}",
             izoh='Usta shaxsiy so\'rovni rad etdi', request=request)
    xabarnomalar.navbatga_tushdi(tamir)
    messages.info(request, 'Ish umumiy navbatga qaytarildi.')
    return redirect('navbat')


@rol_kerak(ADMIN, USTA)
def ishni_boshlash(request, pk):
    tamir = _tamir_ol(request, pk)
    if request.method != 'POST' or not _holat_tekshir(request, tamir, Holat.TASHXIS):
        return redirect(tamir)
    if request.user.is_usta and not _mening_ishim(request, tamir):
        raise PermissionDenied('Bu ta\'mir sizga biriktirilmagan.')

    tamir.holat_ozgartir(Holat.TAMIRDA, user=request.user)
    amal_yoz(request.user, AmalTarixi.Amal.HOLAT, obyekt=f"Ta'mir #{tamir.pk}",
             izoh="Ta'mir boshlandi", request=request)
    messages.success(request, 'Ta\'mir boshlandi.')
    return redirect(tamir)


@rol_kerak(ADMIN, USTA)
def ishni_yakunlash(request, pk):
    tamir = _tamir_ol(request, pk)
    if request.method != 'POST' or not _holat_tekshir(request, tamir, Holat.TAMIRDA):
        return redirect(tamir)
    if request.user.is_usta and not _mening_ishim(request, tamir):
        raise PermissionDenied('Bu ta\'mir sizga biriktirilmagan.')

    form = YakunlashForm(request.POST, instance=tamir, prefix='yak')
    if not form.is_valid():
        return _batafsil_javob(request, tamir, yakunlash_form=form, yakunlash_ochiq=True)

    tamir = form.save(commit=False)
    tamir.holat_ozgartir(Holat.TAYYOR, user=request.user)
    amal_yoz(request.user, AmalTarixi.Amal.HOLAT, obyekt=f"Ta'mir #{tamir.pk}",
             izoh='Ish yakunlandi', request=request)
    xabarnomalar.tayyor(tamir)
    messages.success(request, 'Ish yakunlandi. Operator qurilmani xodimga topshiradi.')
    return redirect(tamir)


# --- Xodim amallari ---

@rol_kerak(XODIM)
def baho_berish(request, pk):
    tamir = _tamir_ol(request, pk)
    if request.method != 'POST':
        return redirect(tamir)
    if not tamir.baho_kutilmoqda:
        messages.error(request, 'Bu ta\'mirni baholab bo\'lmaydi.')
        return redirect(tamir)

    form = BahoForm(request.POST, instance=tamir, prefix='baho')
    if not form.is_valid():
        return _batafsil_javob(request, tamir, baho_form=form, baho_ochiq=True)

    tamir = form.save(commit=False)
    tamir.baho_sana = timezone.now()
    tamir.save()

    amal_yoz(request.user, AmalTarixi.Amal.TAHRIRLASH, obyekt=f"Ta'mir #{tamir.pk}",
             izoh=f'Baho: {tamir.baho}', request=request)
    if tamir.baho <= 2:
        xabarnomalar.past_baho(tamir)
    messages.success(request, 'Bahoyingiz uchun rahmat!')
    return redirect(tamir)


# --- Admin amallari ---

@rol_kerak(ADMIN)
def tasdiq_qarori(request, pk):
    """«O'zim ta'mirladim» hisobotini tasdiqlash yoki rad etish."""
    tamir = _tamir_ol(request, pk)
    if request.method != 'POST':
        return redirect(tamir)
    if not tamir.ozi_tamiri or tamir.tasdiq_holati != Tasdiq.KUTILMOQDA:
        messages.error(request, 'Bu yozuv tasdiqlashni kutmayapti.')
        return redirect(tamir)

    form = TasdiqForm(request.POST, prefix='tas')
    if not form.is_valid():
        return _batafsil_javob(request, tamir, tasdiq_form=form, tasdiq_ochiq=True)

    tamir.tasdiq_holati = form.cleaned_data['qaror']
    tamir.tasdiq_izohi = form.cleaned_data['izoh']
    tamir.tasdiqlagan = request.user
    tamir.tasdiq_sana = timezone.now()
    tamir._ozgartirgan_user = request.user
    tamir.save()

    tasdiqlandi = tamir.tasdiq_holati == Tasdiq.TASDIQLANDI
    amal_yoz(request.user,
             AmalTarixi.Amal.TASDIQLASH if tasdiqlandi else AmalTarixi.Amal.RAD,
             obyekt=f"O'zi ta'mirlagan #{tamir.pk}", izoh=tamir.tasdiq_izohi, request=request)
    xabarnomalar.ozi_tamir_qarori(tamir)
    messages.success(
        request, 'Hisobot tasdiqlandi.' if tasdiqlandi else 'Hisobot rad etildi.',
    )
    return redirect('tasdiqlash_navbati')
