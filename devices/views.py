from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import AmalTarixi
from accounts.permissions import ADMIN, OPERATOR, USTA, XODIM, rol_kerak
from accounts.utils import amal_yoz

from .excel import SARLAVHALAR, import_qil, shablon_yarat
from .forms import BolimForm, ImportForm, QurilmaForm, XodimForm
from .models import Bolim, Qurilma, Xodim
from .qr import qr_png

QR_CHOP_CHEGARA = 500


def _qurilmalarni_saralash(request, qs):
    """Qidiruv va filtrlarni qo'llaydi; tanlangan qiymatlarni ham qaytaradi."""
    q = request.GET.get('q', '').strip()
    turi = request.GET.get('turi', '')
    bolim = request.GET.get('bolim', '')
    holati = request.GET.get('holati', '')

    if q:
        qs = qs.filter(
            Q(inventar_raqami__icontains=q)
            | Q(modeli__icontains=q)
            | Q(seriya_raqami__icontains=q)
        )
    if turi:
        qs = qs.filter(turi=turi)
    if bolim:
        qs = qs.filter(bolim_id=bolim)
    if holati:
        qs = qs.filter(holati=holati)

    return qs, {'q': q, 'turi': turi, 'bolim': bolim, 'holati': holati}


def _sorov_qatori(request):
    """Sahifalash havolalari uchun joriy filtrlarni saqlab qoladi."""
    parametrlar = request.GET.copy()
    parametrlar.pop('page', None)
    qator = parametrlar.urlencode()
    return f'&{qator}' if qator else ''


def _xodim_qurilmalari(user):
    """Xodim faqat o'ziga va o'z bo'limiga tegishli qurilmalarni ko'radi."""
    xodim = user.xodim_profili
    if xodim is None:
        return Qurilma.objects.none()
    return Qurilma.objects.filter(Q(xodim=xodim) | Q(bolim=xodim.bolim))


# --- Qurilmalar ---

@rol_kerak(ADMIN, OPERATOR, USTA, XODIM)
def qurilma_royxati(request):
    if request.user.is_xodim:
        qs = _xodim_qurilmalari(request.user)
        sarlavha = 'Mening qurilmalarim'
    else:
        qs = Qurilma.objects.all()
        sarlavha = 'Qurilmalar'

    qs, tanlangan = _qurilmalarni_saralash(request, qs.select_related('bolim', 'xodim'))
    sahifa = Paginator(qs, 25).get_page(request.GET.get('page'))

    return render(request, 'devices/qurilma_royxati.html', {
        'sahifa': sahifa,
        'sarlavha': sarlavha,
        'jami': qs.count(),
        'turlar': Qurilma.Turi.choices,
        'holatlar': Qurilma.Holat.choices,
        'bolimlar': Bolim.objects.all(),
        'sorov': _sorov_qatori(request),
        **tanlangan,
    })


def _qurilma_ol(request, pk, *, select_related=()):
    """Qurilmani oladi; xodim faqat o'ziga tegishlisini ko'ra oladi."""
    qs = Qurilma.objects.select_related(*select_related) if select_related else Qurilma.objects
    qurilma = get_object_or_404(qs, pk=pk)
    if request.user.is_xodim and not _xodim_qurilmalari(request.user).filter(pk=pk).exists():
        raise PermissionDenied('Bu qurilma sizga biriktirilmagan.')
    return qurilma


@rol_kerak(ADMIN, OPERATOR, USTA, XODIM)
def qurilma_batafsil(request, pk):
    qurilma = _qurilma_ol(request, pk, select_related=('bolim', 'xodim'))
    tamirlar = qurilma.tamirlar.select_related('usta', 'xodim').order_by('-qabul_sana')
    return render(request, 'devices/qurilma_batafsil.html', {
        'qurilma': qurilma,
        'tamirlar': tamirlar,
    })


@rol_kerak(ADMIN, OPERATOR)
def qurilma_yangi(request):
    form = QurilmaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        qurilma = form.save()
        amal_yoz(request.user, AmalTarixi.Amal.YARATISH,
                 obyekt=f'Qurilma {qurilma.inventar_raqami}', request=request)
        messages.success(request, f'«{qurilma.inventar_raqami}» qurilmasi qo\'shildi.')
        return redirect(qurilma)

    return render(request, 'devices/qurilma_form.html', {'form': form, 'yangi': True})


@rol_kerak(ADMIN, OPERATOR)
def qurilma_tahrirlash(request, pk):
    qurilma = get_object_or_404(Qurilma, pk=pk)
    form = QurilmaForm(request.POST or None, instance=qurilma)
    if request.method == 'POST' and form.is_valid():
        form.save()
        amal_yoz(request.user, AmalTarixi.Amal.TAHRIRLASH,
                 obyekt=f'Qurilma {qurilma.inventar_raqami}', request=request)
        messages.success(request, 'Qurilma ma\'lumotlari saqlandi.')
        return redirect(qurilma)

    return render(request, 'devices/qurilma_form.html', {'form': form, 'qurilma': qurilma})


@rol_kerak(ADMIN, OPERATOR)
def qurilma_holat(request, pk):
    """Qurilmani yaroqsizga chiqarish yoki ishlaydiganlar qatoriga qaytarish."""
    qurilma = get_object_or_404(Qurilma, pk=pk)
    if request.method != 'POST':
        return redirect(qurilma)

    yangi = request.POST.get('holati')
    if yangi not in Qurilma.Holat.values:
        messages.error(request, 'Noto\'g\'ri holat tanlandi.')
        return redirect(qurilma)

    eski = qurilma.get_holati_display()
    qurilma.holati = yangi
    qurilma.save(update_fields=['holati'])
    amal_yoz(request.user, AmalTarixi.Amal.HOLAT,
             obyekt=f'Qurilma {qurilma.inventar_raqami}',
             izoh=f'{eski} → {qurilma.get_holati_display()}', request=request)
    messages.success(request, f'Holat o\'zgartirildi: {qurilma.get_holati_display()}.')
    return redirect(qurilma)


@rol_kerak(ADMIN, OPERATOR, USTA, XODIM)
def qurilma_qr(request, pk):
    """Qurilma sahifasiga olib boradigan QR-kod rasmi."""
    qurilma = _qurilma_ol(request, pk)
    manzil = request.build_absolute_uri(qurilma.get_absolute_url())
    return HttpResponse(qr_png(manzil), content_type='image/png')


@rol_kerak(ADMIN, OPERATOR)
def qr_chop(request):
    """Qurilmalarga yopishtirish uchun QR-yorliqlar (chop etish sahifasi)."""
    qs, tanlangan = _qurilmalarni_saralash(
        request, Qurilma.objects.select_related('bolim'),
    )
    jami = qs.count()
    qurilmalar = qs[:QR_CHOP_CHEGARA]

    return render(request, 'devices/qr_chop.html', {
        'qurilmalar': qurilmalar,
        'jami': jami,
        'chegara': QR_CHOP_CHEGARA,
        'kesildi': jami > QR_CHOP_CHEGARA,
        'turlar': Qurilma.Turi.choices,
        'holatlar': Qurilma.Holat.choices,
        'bolimlar': Bolim.objects.all(),
        **tanlangan,
    })


# --- Excel import ---

def _import_sahifasi(request, tur, qaytish_url, sarlavha):
    form = ImportForm(request.POST or None, request.FILES or None)
    natija = None

    if request.method == 'POST' and form.is_valid():
        natija = import_qil(
            form.cleaned_data['fayl'], tur, yangilash=form.cleaned_data['yangilash'],
        )
        amal_yoz(
            request.user, AmalTarixi.Amal.YARATISH, obyekt=f'Excel import: {sarlavha}',
            izoh=(f'yaratildi={natija.yaratildi}, yangilandi={natija.yangilandi}, '
                  f"o'tkazildi={natija.otkazildi}, xato={len(natija.xatolar)}"),
            request=request,
        )
        if natija.yaratildi or natija.yangilandi:
            messages.success(
                request,
                f'Import tugadi: {natija.yaratildi} ta yangi, {natija.yangilandi} ta yangilandi.',
            )

    return render(request, 'devices/import.html', {
        'form': form,
        'natija': natija,
        'tur': tur,
        'sarlavha': sarlavha,
        'qaytish_url': qaytish_url,
    })


@rol_kerak(ADMIN)
def qurilma_import(request):
    return _import_sahifasi(request, 'qurilma', 'qurilma_royxati', 'Qurilmalar')


@rol_kerak(ADMIN)
def xodim_import(request):
    return _import_sahifasi(request, 'xodim', 'xodim_royxati', 'Xodimlar')


@rol_kerak(ADMIN)
def shablon_yuklab_olish(request, tur):
    if tur not in SARLAVHALAR:
        raise PermissionDenied('Noma\'lum shablon turi.')
    javob = HttpResponse(
        shablon_yarat(tur),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    javob['Content-Disposition'] = f'attachment; filename="{tur}_shablon.xlsx"'
    return javob


# --- Bo'limlar ---

@rol_kerak(ADMIN)
def bolim_royxati(request):
    bolimlar = Bolim.objects.annotate(
        qurilmalar_soni=Count('qurilmalar', distinct=True),
        xodimlar_soni=Count('xodimlar', distinct=True),
    )
    return render(request, 'devices/bolim_royxati.html', {'bolimlar': bolimlar})


@rol_kerak(ADMIN)
def bolim_yangi(request):
    form = BolimForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        bolim = form.save()
        amal_yoz(request.user, AmalTarixi.Amal.YARATISH,
                 obyekt=f"Bo'lim {bolim.nomi}", request=request)
        messages.success(request, f'«{bolim.nomi}» bo\'limi qo\'shildi.')
        return redirect('bolim_royxati')
    return render(request, 'devices/oddiy_form.html', {
        'form': form, 'sarlavha': "Yangi bo'lim", 'qaytish_url': 'bolim_royxati',
    })


@rol_kerak(ADMIN)
def bolim_tahrirlash(request, pk):
    bolim = get_object_or_404(Bolim, pk=pk)
    form = BolimForm(request.POST or None, instance=bolim)
    if request.method == 'POST' and form.is_valid():
        form.save()
        amal_yoz(request.user, AmalTarixi.Amal.TAHRIRLASH,
                 obyekt=f"Bo'lim {bolim.nomi}", request=request)
        messages.success(request, 'Saqlandi.')
        return redirect('bolim_royxati')
    return render(request, 'devices/oddiy_form.html', {
        'form': form, 'sarlavha': f"Bo'lim: {bolim.nomi}", 'qaytish_url': 'bolim_royxati',
    })


# --- Xodimlar ---

@rol_kerak(ADMIN)
def xodim_royxati(request):
    qs = Xodim.objects.select_related('bolim', 'user')

    q = request.GET.get('q', '').strip()
    bolim = request.GET.get('bolim', '')
    if q:
        qs = qs.filter(Q(fio__icontains=q) | Q(telefon__icontains=q) | Q(lavozimi__icontains=q))
    if bolim:
        qs = qs.filter(bolim_id=bolim)

    sahifa = Paginator(qs, 25).get_page(request.GET.get('page'))
    return render(request, 'devices/xodim_royxati.html', {
        'sahifa': sahifa,
        'jami': qs.count(),
        'bolimlar': Bolim.objects.all(),
        'q': q,
        'bolim': bolim,
        'sorov': _sorov_qatori(request),
    })


@rol_kerak(ADMIN)
def xodim_yangi(request):
    form = XodimForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        xodim = form.save()
        amal_yoz(request.user, AmalTarixi.Amal.YARATISH,
                 obyekt=f'Xodim {xodim.fio}', request=request)
        messages.success(request, f'«{xodim.fio}» qo\'shildi.')
        return redirect('xodim_royxati')
    return render(request, 'devices/oddiy_form.html', {
        'form': form, 'sarlavha': 'Yangi xodim', 'qaytish_url': 'xodim_royxati',
    })


@rol_kerak(ADMIN)
def xodim_tahrirlash(request, pk):
    xodim = get_object_or_404(Xodim, pk=pk)
    form = XodimForm(request.POST or None, instance=xodim)
    if request.method == 'POST' and form.is_valid():
        form.save()
        amal_yoz(request.user, AmalTarixi.Amal.TAHRIRLASH,
                 obyekt=f'Xodim {xodim.fio}', request=request)
        messages.success(request, 'Saqlandi.')
        return redirect('xodim_royxati')
    return render(request, 'devices/oddiy_form.html', {
        'form': form, 'sarlavha': f'Xodim: {xodim.fio}', 'qaytish_url': 'xodim_royxati',
    })
