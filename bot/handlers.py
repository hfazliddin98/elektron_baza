"""Telegram bot buyruqlari va dialoglari (aiogram 3).

Ishga tushirish:  python manage.py bot
"""

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,
    Message, ReplyKeyboardMarkup, ReplyKeyboardRemove,
)
from asgiref.sync import sync_to_async

from . import baza

logger = logging.getLogger(__name__)
router = Router()

TUGMA_MUROJAAT = "🛠 Ta'mirga murojaat"
TUGMA_MENING = '📋 Mening murojaatlarim'
TUGMA_YORDAM = 'ℹ️ Yordam'
TUGMA_NAVBAT = '📥 Navbat'
TUGMA_ISHLARIM = "🔧 Mening ishlarim"
TUGMA_BEKOR = '❌ Bekor qilish'


def xodim_menyusi():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TUGMA_MUROJAAT)],
            [KeyboardButton(text=TUGMA_MENING), KeyboardButton(text=TUGMA_YORDAM)],
        ],
        resize_keyboard=True,
    )


def usta_menyusi():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TUGMA_NAVBAT), KeyboardButton(text=TUGMA_ISHLARIM)],
            [KeyboardButton(text=TUGMA_YORDAM)],
        ],
        resize_keyboard=True,
    )


def bekor_menyusi():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TUGMA_BEKOR)]], resize_keyboard=True,
    )


class Murojaat(StatesGroup):
    qurilma = State()
    muammo = State()
    muhimlik = State()
    usta = State()


# --- Ro'yxatdan o'tish ---

@router.message(CommandStart())
async def boshlash(xabar: Message, state: FSMContext):
    await state.clear()
    xodim = await sync_to_async(baza.xodim_top)(xabar.from_user.id)
    if xodim:
        await xabar.answer(
            f'Assalomu alaykum, {xodim.fio}!\nQuyidagi tugmalardan foydalaning.',
            reply_markup=xodim_menyusi(),
        )
        return

    usta = await sync_to_async(baza.usta_top)(xabar.from_user.id)
    if usta:
        await xabar.answer(
            f'Assalomu alaykum, {usta.fio}!\nQuyidagi tugmalardan foydalaning.',
            reply_markup=usta_menyusi(),
        )
        return

    klaviatura = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='📱 Telefon raqamimni yuborish', request_contact=True)]],
        resize_keyboard=True,
    )
    await xabar.answer(
        'Assalomu alaykum! Bu — universitet qurilmalarini ta\'mirlash tizimi boti.\n\n'
        'Sizni tizimdagi profilingizga ulash uchun telefon raqamingizni yuboring.',
        reply_markup=klaviatura,
    )


@router.message(F.contact)
async def kontakt(xabar: Message):
    tur, obyekt = await sync_to_async(baza.foydalanuvchini_bogla)(
        xabar.from_user.id, xabar.contact.phone_number,
    )
    if tur is None:
        await xabar.answer(
            'Bu raqam tizimda topilmadi. Administratorga murojaat qilib, '
            'telefon raqamingizni tizimga kiritishni so\'rang.',
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    menyu = xodim_menyusi() if tur == 'xodim' else usta_menyusi()
    await xabar.answer(f'Tayyor, {obyekt.fio}! Hisobingiz ulandi.', reply_markup=menyu)


@router.message(Command('yordam'))
@router.message(F.text == TUGMA_YORDAM)
async def yordam(xabar: Message):
    await xabar.answer(
        "<b>Bot imkoniyatlari</b>\n\n"
        f"{TUGMA_MUROJAAT} — nosoz qurilma haqida murojaat yuborish\n"
        f"{TUGMA_MENING} — murojaatlaringiz holatini ko'rish\n"
        f"{TUGMA_NAVBAT} — (ustalar uchun) navbatdagi ishlar\n\n"
        "Qurilma topshirilgach bot sizdan xizmatni baholashni so'raydi.\n"
        "/start — hisobni qayta ulash",
    )


@router.message(F.text == TUGMA_BEKOR)
async def bekor(xabar: Message, state: FSMContext):
    await state.clear()
    xodim = await sync_to_async(baza.xodim_top)(xabar.from_user.id)
    await xabar.answer('Bekor qilindi.',
                       reply_markup=xodim_menyusi() if xodim else usta_menyusi())


# --- Murojaat yuborish ---

@router.message(F.text == TUGMA_MUROJAAT)
async def murojaat_boshla(xabar: Message, state: FSMContext):
    xodim = await sync_to_async(baza.xodim_top)(xabar.from_user.id)
    if xodim is None:
        await xabar.answer("Avval /start orqali hisobingizni ulang.")
        return

    qurilmalar = await sync_to_async(baza.xodim_qurilmalari)(xodim)
    if not qurilmalar:
        await xabar.answer("Bo'limingizga biriktirilgan qurilma topilmadi. "
                           'Administratorga murojaat qiling.')
        return

    tugmalar = [[InlineKeyboardButton(
        text=f'{q.inventar_raqami} — {q.get_turi_display()}', callback_data=f'qurilma:{q.pk}',
    )] for q in qurilmalar]

    await state.set_state(Murojaat.qurilma)
    await xabar.answer('Qaysi qurilma nosoz?', reply_markup=bekor_menyusi())
    await xabar.answer('Ro\'yxatdan tanlang:',
                       reply_markup=InlineKeyboardMarkup(inline_keyboard=tugmalar))


@router.callback_query(Murojaat.qurilma, F.data.startswith('qurilma:'))
async def qurilma_tanlandi(sorov: CallbackQuery, state: FSMContext):
    qurilma_id = int(sorov.data.split(':')[1])
    qurilma = await sync_to_async(baza.qurilma_top)(qurilma_id)
    if qurilma is None:
        await sorov.answer('Qurilma topilmadi', show_alert=True)
        return

    await state.update_data(qurilma_id=qurilma_id)
    await state.set_state(Murojaat.muammo)
    await sorov.message.answer(
        f'Tanlandi: <b>{qurilma.inventar_raqami}</b>\n\n'
        'Endi muammoni yozing (imkon qadar aniq).',
    )
    await sorov.answer()


@router.message(Murojaat.muammo, F.text)
async def muammo_yozildi(xabar: Message, state: FSMContext):
    matn = xabar.text.strip()
    if len(matn) < 5:
        await xabar.answer('Muammoni biroz batafsilroq yozing.')
        return

    await state.update_data(muammo=matn)
    await state.set_state(Murojaat.muhimlik)
    tugmalar = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Oddiy', callback_data='muhim:oddiy'),
        InlineKeyboardButton(text='🔴 Shoshilinch', callback_data='muhim:shoshilinch'),
    ]])
    await xabar.answer('Muammo qanchalik shoshilinch?', reply_markup=tugmalar)


@router.callback_query(Murojaat.muhimlik, F.data.startswith('muhim:'))
async def muhimlik_tanlandi(sorov: CallbackQuery, state: FSMContext):
    await state.update_data(shoshilinch=sorov.data.endswith('shoshilinch'))
    await state.set_state(Murojaat.usta)

    ustalar = await sync_to_async(baza.faol_ustalar)()
    tugmalar = [[InlineKeyboardButton(text=u.fio, callback_data=f'usta:{u.pk}')] for u in ustalar]
    tugmalar.append([InlineKeyboardButton(text='Farqi yo\'q', callback_data='usta:0')])

    await sorov.message.answer(
        'Ustani o\'zingiz tanlaysizmi? «Farqi yo\'q» desangiz ish umumiy navbatga tushadi.',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=tugmalar),
    )
    await sorov.answer()


@router.callback_query(Murojaat.usta, F.data.startswith('usta:'))
async def usta_tanlandi(sorov: CallbackQuery, state: FSMContext):
    usta_id = int(sorov.data.split(':')[1]) or None
    malumot = await state.get_data()
    await state.clear()

    xodim = await sync_to_async(baza.xodim_top)(sorov.from_user.id)
    if xodim is None:
        await sorov.answer('Hisobingiz ulanmagan', show_alert=True)
        return

    tamir = await sync_to_async(baza.murojaat_yarat)(
        xodim, malumot['qurilma_id'], malumot['muammo'],
        shoshilinch=malumot.get('shoshilinch', False), usta_id=usta_id,
    )
    await sorov.message.answer(
        f'✅ Murojaatingiz qabul qilindi. Raqami: <b>#{tamir.pk}</b>\n'
        'Holati o\'zgarganda sizga xabar beramiz.',
        reply_markup=xodim_menyusi(),
    )
    await sorov.answer()


# --- Ro'yxatlar ---

@router.message(F.text == TUGMA_MENING)
async def mening_murojaatlarim(xabar: Message):
    xodim = await sync_to_async(baza.xodim_top)(xabar.from_user.id)
    if xodim is None:
        await xabar.answer("Avval /start orqali hisobingizni ulang.")
        return

    tamirlar = await sync_to_async(baza.mening_murojaatlarim)(xodim)
    if not tamirlar:
        await xabar.answer('Sizda murojaat yo\'q.')
        return

    qatorlar = [
        f'<b>#{t.pk}</b> {t.qurilma.inventar_raqami} — {t.holat_nomi}'
        + (f'\n   Usta: {t.usta.fio}' if t.usta else '')
        for t in tamirlar
    ]
    await xabar.answer('<b>Oxirgi murojaatlaringiz:</b>\n\n' + '\n'.join(qatorlar))

    for tamir in tamirlar:
        if tamir.baho_kutilmoqda:
            await xabar.answer(
                f'#{tamir.pk} ta\'miri baholanmagan. Xizmatni baholang:',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text=str(b), callback_data=f'baho:{tamir.pk}:{b}')
                    for b in range(1, 6)
                ]]),
            )


@router.message(F.text == TUGMA_NAVBAT)
async def navbat(xabar: Message):
    usta = await sync_to_async(baza.usta_top)(xabar.from_user.id)
    if usta is None:
        await xabar.answer('Bu bo\'lim faqat ustalar uchun.')
        return

    soralgan, erkin = await sync_to_async(baza.usta_navbati)(usta)
    qismlar = []
    if soralgan:
        qismlar.append('<b>Sizdan so\'ralgan ishlar:</b>\n' + '\n'.join(
            f'#{t.pk} {t.qurilma.inventar_raqami} — {t.muammo_tavsifi[:60]}' for t in soralgan))
    if erkin:
        qismlar.append('<b>Umumiy navbat:</b>\n' + '\n'.join(
            ('🔴 ' if t.muhimlik == t.Muhimlik.SHOSHILINCH else '')
            + f'#{t.pk} {t.qurilma.inventar_raqami} — {t.muammo_tavsifi[:60]}' for t in erkin))

    if not qismlar:
        await xabar.answer('Navbat bo\'sh.')
        return
    await xabar.answer('\n\n'.join(qismlar) + '\n\nIshni saytdagi «Navbat» bo\'limidan oling.')


@router.message(F.text == TUGMA_ISHLARIM)
async def ishlarim(xabar: Message):
    usta = await sync_to_async(baza.usta_top)(xabar.from_user.id)
    if usta is None:
        await xabar.answer('Bu bo\'lim faqat ustalar uchun.')
        return

    ishlar = await sync_to_async(baza.usta_ishlari)(usta)
    if not ishlar:
        await xabar.answer('Hozir sizda aktiv ish yo\'q.')
        return

    await xabar.answer('<b>Aktiv ishlaringiz:</b>\n\n' + '\n'.join(
        f'#{t.pk} {t.qurilma.inventar_raqami} — {t.holat_nomi}\n   {t.muammo_tavsifi[:60]}'
        for t in ishlar
    ))


# --- Baholash ---

@router.callback_query(F.data.startswith('baho:'))
async def baho(sorov: CallbackQuery):
    _, tamir_id, qiymat = sorov.data.split(':')
    muvaffaqiyat, xabar_matni = await sync_to_async(baza.baho_qoy)(
        sorov.from_user.id, int(tamir_id), int(qiymat),
    )
    await sorov.answer(xabar_matni, show_alert=not muvaffaqiyat)
    if muvaffaqiyat:
        await sorov.message.edit_text(f'{sorov.message.text}\n\n⭐ Bahoyingiz: {qiymat}/5')


@router.message()
async def tushunarsiz(xabar: Message):
    await xabar.answer('Tushunmadim. Tugmalardan foydalaning yoki /yordam yuboring.')
