"""Ta'mirlash jarayonidagi Telegram xabarnomalari.

Barcha xabarlar shu yerda to'plangan — matnni o'zgartirish uchun faqat shu
faylni tahrirlash kifoya. Telegram sozlanmagan bo'lsa funksiyalar jimgina
hech narsa qilmaydi.
"""

from bot import xabar


def _tavsif(tamir):
    return (f'<b>{tamir.qurilma.inventar_raqami}</b> — {tamir.qurilma.get_turi_display()}\n'
            f'Muammo: {tamir.muammo_tavsifi[:200]}')


def yangi_murojaat(tamir):
    """Operator/admin guruhiga: yangi murojaat keldi."""
    belgi = '🔴 SHOSHILINCH\n' if tamir.muhimlik == tamir.Muhimlik.SHOSHILINCH else ''
    xabar.adminlarga(
        f'{belgi}📥 Yangi murojaat #{tamir.pk}\n{_tavsif(tamir)}\n'
        f'Xodim: {tamir.xodim.fio}'
    )


def qabul_qilindi(tamir):
    xabar.xodimga(
        tamir.xodim,
        f'✅ Murojaatingiz #{tamir.pk} qabul qilindi.\n{_tavsif(tamir)}\n'
        'Usta tayinlangach yana xabar beramiz.',
    )


def rad_etildi(tamir):
    xabar.xodimga(
        tamir.xodim,
        f'❌ Murojaatingiz #{tamir.pk} rad etildi.\nSabab: {tamir.rad_sababi}',
    )


def navbatga_tushdi(tamir):
    """Ustalarga: navbatda yangi ish bor."""
    if tamir.tanlangan_usta:
        xabar.ustaga(
            tamir.tanlangan_usta,
            f'👤 Sizdan shaxsan so\'ralgan ta\'mir #{tamir.pk}\n{_tavsif(tamir)}\n'
            'Saytdagi «Navbat» bo\'limidan qabul qiling yoki rad eting.',
        )
        return
    belgi = '🔴 SHOSHILINCH\n' if tamir.muhimlik == tamir.Muhimlik.SHOSHILINCH else ''
    xabar.ustalarga(f'{belgi}🛠 Navbatda yangi ish #{tamir.pk}\n{_tavsif(tamir)}')


def ustaga_biriktirildi(tamir):
    xabar.ustaga(
        tamir.usta,
        f'🛠 Sizga ta\'mir biriktirildi: #{tamir.pk}\n{_tavsif(tamir)}',
    )
    xabar.xodimga(
        tamir.xodim,
        f'🔧 Murojaatingiz #{tamir.pk} ta\'mirga olindi.\nUsta: {tamir.usta.fio}',
    )


def tayyor(tamir):
    xabar.xodimga(
        tamir.xodim,
        f'📦 Qurilmangiz tayyor: {tamir.qurilma.inventar_raqami}\n'
        f'Ta\'mir #{tamir.pk} yakunlandi — olib ketishingiz mumkin.',
    )


def topshirildi(tamir):
    xabar.xodimga(
        tamir.xodim,
        f'✅ Qurilmangiz topshirildi: {tamir.qurilma.inventar_raqami}\n'
        'Iltimos, xizmatni baholang (1–5).',
        tugmalar=[[{'text': str(b), 'callback_data': f'baho:{tamir.pk}:{b}'} for b in range(1, 6)]],
    )


def baho_eslatmasi(tamir):
    xabar.xodimga(
        tamir.xodim,
        f'⭐ #{tamir.pk} ta\'miri uchun bahoyingizni kutmoqdamiz.\n'
        f'{tamir.qurilma.inventar_raqami} — {tamir.qurilma.get_turi_display()}',
        tugmalar=[[{'text': str(b), 'callback_data': f'baho:{tamir.pk}:{b}'} for b in range(1, 6)]],
    )


def past_baho(tamir):
    xabar.adminlarga(
        f'⚠️ Past baho ({tamir.baho}/5) — ta\'mir #{tamir.pk}\n'
        f'Usta: {tamir.usta.fio if tamir.usta else "—"}\n'
        f'Izoh: {tamir.baho_izoh or "—"}'
    )


def ozi_tamir_yuborildi(tamir):
    xabar.adminlarga(
        f'📝 «O\'zim ta\'mirladim» hisoboti #{tamir.pk} tasdiq kutmoqda.\n'
        f'{_tavsif(tamir)}\nXodim: {tamir.xodim.fio}'
    )


def ozi_tamir_qarori(tamir):
    if tamir.tasdiq_holati == tamir.Tasdiq.TASDIQLANDI:
        matn = f'✅ «O\'zim ta\'mirladim» hisobotingiz #{tamir.pk} tasdiqlandi.'
    else:
        matn = (f'❌ «O\'zim ta\'mirladim» hisobotingiz #{tamir.pk} rad etildi.\n'
                f'Sabab: {tamir.tasdiq_izohi or "—"}')
    xabar.xodimga(tamir.xodim, matn)


def sla_ogohlantirish(kechikkanlar):
    """Adminlarga: muddati o'tgan ta'mirlar ro'yxati."""
    if not kechikkanlar:
        return
    qatorlar = [
        f'• #{t.pk} {t.qurilma.inventar_raqami} — {t.get_holat_display()} '
        f'({t.kechikkan_kun} kun kechikkan)'
        for t in kechikkanlar[:20]
    ]
    qolgan = len(kechikkanlar) - 20
    if qolgan > 0:
        qatorlar.append(f'... va yana {qolgan} ta')
    xabar.adminlarga('⏰ Muddati o\'tgan ta\'mirlar:\n' + '\n'.join(qatorlar))
