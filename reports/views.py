from datetime import date, timedelta
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa

from accounts.models import AmalTarixi
from accounts.permissions import ADMIN, RAHBARIYAT, rol_kerak
from accounts.utils import amal_yoz

from . import hisobot as hisobot_moduli
from .excel import hisobot_excel as excel_yarat

HISOBOT_ROLLARI = (ADMIN, RAHBARIYAT)


def _sana(matn):
    try:
        return date.fromisoformat(matn)
    except (TypeError, ValueError):
        return None


def _davr(request):
    return hisobot_moduli.davr_aniqla(
        _sana(request.GET.get('dan')), _sana(request.GET.get('gacha')),
    )


def _tez_havolalar():
    bugun = timezone.localdate()
    shu_oy = bugun.replace(day=1)
    otgan_oy_oxiri = shu_oy - timedelta(days=1)
    return [
        ('Shu oy', shu_oy, bugun),
        ("O'tgan oy", otgan_oy_oxiri.replace(day=1), otgan_oy_oxiri),
        ('Shu yil', bugun.replace(month=1, day=1), bugun),
        ("O'tgan yil", date(bugun.year - 1, 1, 1), date(bugun.year - 1, 12, 31)),
    ]


@rol_kerak(*HISOBOT_ROLLARI)
def hisobot(request):
    davr = _davr(request)
    malumot = hisobot_moduli.yig(davr)

    oylar = malumot['oylar']
    return render(request, 'reports/hisobot.html', {
        **malumot,
        'dan': davr.boshlanish.isoformat(),
        'gacha': davr.tugash.isoformat(),
        'tez_havolalar': _tez_havolalar(),
        # `json_script` shablon filtri o'zi JSON'ga o'girib beradi
        'diagramma': {
            'oylar': [o['nomi'] for o in oylar],
            'kelgan': [o['kelgan'] for o in oylar],
            'tugatilgan': [o['tugatilgan'] for o in oylar],
            'ustalar': [u.fio for u in malumot['ustalar'] if u.tamirlar_soni],
            'usta_soni': [u.tamirlar_soni for u in malumot['ustalar'] if u.tamirlar_soni],
            'usta_reyting': [round(u.reyting, 2) if u.reyting else 0
                             for u in malumot['ustalar'] if u.tamirlar_soni],
            'manba_nomlari': [m['nomi'] for m in malumot['manbalar']],
            'manba_soni': [m['soni'] for m in malumot['manbalar']],
        },
    })


@rol_kerak(*HISOBOT_ROLLARI)
def hisobot_excel(request):
    davr = _davr(request)
    malumot = hisobot_moduli.yig(davr)

    amal_yoz(request.user, AmalTarixi.Amal.YARATISH,
             obyekt='Hisobot (Excel)', izoh=davr.nomi, request=request)

    javob = HttpResponse(
        excel_yarat(malumot),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    nom = f'hisobot_{davr.boshlanish:%Y%m%d}_{davr.tugash:%Y%m%d}.xlsx'
    javob['Content-Disposition'] = f'attachment; filename="{nom}"'
    return javob


@rol_kerak(*HISOBOT_ROLLARI)
def hisobot_pdf(request):
    davr = _davr(request)
    malumot = hisobot_moduli.yig(davr)

    # xhtml2pdf statik fayllarni faqat to'liq yo'l bo'yicha topadi
    logo = Path(settings.BASE_DIR) / 'static' / 'img' / 'logo.png'

    html = render_to_string('reports/hisobot_pdf.html', {
        **malumot,
        'tayyorlandi': timezone.localtime(),
        'tayyorlagan': request.user.get_full_name() or request.user.username,
        'logo_yoli': logo.as_uri() if logo.exists() else '',
    })

    bufer = BytesIO()
    natija = pisa.CreatePDF(html, dest=bufer, encoding='utf-8')
    if natija.err:
        return HttpResponse('PDF yaratishda xato yuz berdi.', status=500)

    amal_yoz(request.user, AmalTarixi.Amal.YARATISH,
             obyekt='Hisobot (PDF)', izoh=davr.nomi, request=request)

    javob = HttpResponse(bufer.getvalue(), content_type='application/pdf')
    nom = f'hisobot_{davr.boshlanish:%Y%m%d}_{davr.tugash:%Y%m%d}.pdf'
    javob['Content-Disposition'] = f'attachment; filename="{nom}"'
    return javob
