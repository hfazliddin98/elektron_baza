# Elektron Baza

Universitet elektron qurilmalarini ro'yxatga olish va ta'mirlash jarayonini boshqarish tizimi (CRM).

**Imkoniyatlar (reja bo'yicha):** qurilmalar reestri (Excel import, QR-kod), sayt va Telegram bot orqali ta'mirlash murojaatlari, ustalar navbati, xizmatni baholash, o'zi-ta'mirlash hisobotlari (admin tasdig'i bilan), oylik/yillik hisobotlar (Excel/PDF).

Loyiha bosqichlari: [ETAPLAR.md](ETAPLAR.md)

## Texnologiyalar

- Python 3.14 / Django 6
- PostgreSQL (lokal ishlashda SQLite ham mumkin)
- Bootstrap 5
- aiogram (Telegram bot, 10-bosqichda)

## O'rnatish

```bash
git clone https://github.com/hfazliddin98/elektron_baza.git
cd elektron_baza

# Virtual muhit
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Kutubxonalar
pip install -r requirements.txt

# Sozlamalar
copy .env.example .env       # Windows (Linux/Mac: cp)
# .env ichida SECRET_KEY va (kerak bo'lsa) PostgreSQL ma'lumotlarini to'ldiring
# DB_NAME bo'sh qolsa SQLite ishlatiladi — birinchi ishga tushirish uchun qulay

# Baza va admin foydalanuvchi
python manage.py migrate
python manage.py createsuperuser

# Namunaviy ma'lumotlar (ixtiyoriy, faqat ishlab chiqish uchun)
python manage.py namuna

# Ishga tushirish
python manage.py runserver
```

Sayt: http://127.0.0.1:8000/ · Admin panel: http://127.0.0.1:8000/admin/

`namuna` buyrug'i test uchun foydalanuvchilar yaratadi (**faqat dev muhitida ishlating**):
`admin/admin123`, `operator/operator123`, `rahbar/rahbar123`, `usta1..4/usta123`, `xodim1..6/xodim123`.

## Rollar

| Rol | Huquqlari |
|-----|-----------|
| Admin | hamma narsa + o'zi-ta'mir hisobotlarini tasdiqlash, amallar tarixi |
| Operator | murojaatlarni qabul/rad qilish, shoshilinch ta'mirni biriktirish, topshirish |
| Usta | navbatdan ish olish, o'z ta'mirlarini yuritish |
| Xodim | murojaat yuborish, holatini kuzatish, baholash, o'zi ta'mirlaganini kiritish |
| Rahbariyat | faqat hisobotlarni ko'rish |

View'ga ruxsat qo'yish: `@rol_kerak(ADMIN, OPERATOR)` (`accounts/permissions.py`).
Muhim amallarni tarixga yozish: `amal_yoz(user, AmalTarixi.Amal.TASDIQLASH, obyekt=..., request=request)`.

## Qurilmalar moduli

- **Reestr:** `/qurilmalar/` — qidiruv (inventar raqam, model, seriya), turi/bo'lim/holat bo'yicha filtr.
  Xodim bu sahifada faqat o'ziga va o'z bo'limiga tegishli qurilmalarni ko'radi.
- **Excel import:** `/qurilmalar/import/` va `/xodimlar/import/` (admin uchun).
  Avval shablonni yuklab oling — ustunlar mos kelmasa fayl qabul qilinmaydi.
  Xato qatorlar raqami bilan ko'rsatiladi, qolganlari import qilinadi;
  tuzatilgan faylni qayta yuklash xavfsiz (mavjud yozuvlar takrorlanmaydi).
- **QR-kod:** har qurilma sahifasida QR bor; `/qurilmalar/qr-chop/` — filtrlangan
  yorliqlarni chop etish sahifasi. Skanerlanganda qurilma sahifasi ochiladi.

## Testlar

```bash
python manage.py test
```

## Loyiha tuzilishi

```
config/      — sozlamalar (settings, urls)
accounts/    — foydalanuvchilar, rollar, ustalar
devices/     — bo'limlar, xodimlar, qurilmalar
repairs/     — murojaatlar, ta'mirlash jarayoni, navbat
reports/     — hisobotlar (Excel/PDF)
bot/         — Telegram bot
templates/   — HTML shablonlar (Bootstrap)
static/      — CSS/JS fayllar
```
