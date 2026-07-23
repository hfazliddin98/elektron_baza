# Elektron Baza

Universitet elektron qurilmalarini ro'yxatga olish va ta'mirlash jarayonini boshqarish tizimi (CRM).

**Imkoniyatlari:**

- **Qurilmalar reestri** — qidiruv va filtr, Excel'dan ommaviy import, har qurilmaga QR-kod.
- **Elektron murojaat** — xodim sayt yoki **Telegram bot** orqali ta'mirga murojaat yuboradi;
  istasa ustani o'zi tanlaydi.
- **Navbat** — usta ishni majburiy biriktirilmasdan, navbatning eng eski 10 tasi ichidan
  o'zi tanlab oladi; shoshilinch ishlar tepada turadi.
- **Ta'mirlash jarayoni** — qabul → tashxis → ta'mir → tayyor → topshirish, har bosqich
  tarixi va **SLA muddat nazorati** bilan.
- **Baholash** — xodim xizmatni 1–5 baholaydi, ustalar reytingi shakllanadi.
- **«O'zim ta'mirladim»** — xodim o'zi tuzatgan qurilma bo'yicha hisobot qoldiradi,
  admin tasdiqlaydi.
- **Hisobotlar** — oylik/yillik, ustalar va bo'limlar kesimida, diagrammalar,
  **Excel va PDF** eksport.

Hujjatlar: [Loyiha bosqichlari](ETAPLAR.md) · [Foydalanuvchi qo'llanmasi](QOLLANMA.md) ·
[Serverga o'rnatish](deploy/DEPLOY.md)

## Texnologiyalar

- Python 3.14 / Django 6
- PostgreSQL (lokal ishlashda SQLite ham mumkin)
- Bootstrap 5 + Chart.js
- aiogram 3 (Telegram bot), openpyxl (Excel), qrcode (QR), xhtml2pdf (PDF)

## O'rnatish (ishlab chiqish uchun)

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

Serverga o'rnatish uchun: **[deploy/DEPLOY.md](deploy/DEPLOY.md)**

`namuna` buyrug'i test uchun foydalanuvchilar yaratadi (**faqat dev muhitida ishlating**):
`admin/admin123`, `operator/operator123`, `rahbar/rahbar123`, `usta1..4/usta123`,
`xodim1..6/xodim123`.

## Rollar

| Rol | Huquqlari |
|-----|-----------|
| Admin | hamma narsa + o'zi-ta'mir hisobotlarini tasdiqlash, Excel import, amallar tarixi |
| Operator | murojaatlarni qabul/rad qilish, shoshilinch ta'mirni biriktirish, topshirish |
| Usta | navbatdan ish olish, o'z ta'mirlarini yuritish |
| Xodim | murojaat yuborish, holatini kuzatish, baholash, o'zi ta'mirlaganini kiritish |
| Rahbariyat | faqat hisobotlarni ko'rish |

View'ga ruxsat qo'yish: `@rol_kerak(ADMIN, OPERATOR)` (`accounts/permissions.py`).
Muhim amallarni tarixga yozish: `amal_yoz(user, AmalTarixi.Amal.TASDIQLASH, obyekt=..., request=request)`.

## Loyiha tuzilishi

```
config/      — sozlamalar (settings, urls, umumiy forma yordamchilari)
accounts/    — foydalanuvchilar, rollar, ustalar, amallar tarixi (audit log)
devices/     — bo'limlar, xodimlar, qurilmalar, Excel import, QR-kod
repairs/     — murojaatlar, ta'mirlash jarayoni, navbat, SLA, baholash
reports/     — hisobotlar (HTML, Excel, PDF)
bot/         — Telegram bot va xabarnomalar
templates/   — HTML shablonlar (Bootstrap)
deploy/      — serverga o'rnatish fayllari (systemd, nginx, backup, cron)
```

## Buyruqlar

```bash
python manage.py namuna              # namunaviy ma'lumotlar (faqat dev)
python manage.py bot                 # Telegram botni ishga tushirish
python manage.py kunlik_vazifalar    # SLA ogohlantirish, baho eslatma, avtoyopish
python manage.py kunlik_vazifalar --quruq   # hech narsani o'zgartirmasdan ko'rish
python manage.py test                # barcha testlar (91 ta)
python manage.py check --deploy      # server xavfsizligi tavsiyalari
```

## Modullar

- **Qurilmalar:** `/qurilmalar/` — qidiruv, filtr; `/qurilmalar/import/` — Excel import
  (shablonni yuklab oling, xato qatorlar raqami bilan ko'rsatiladi, qayta yuklash xavfsiz);
  `/qurilmalar/qr-chop/` — QR yorliqlarni chop etish.
- **Murojaatlar:** `/murojaat/yangi/` (xodim), `/murojaatlar/` (operator navbati),
  `/murojaat/ozim/` — «o'zim ta'mirladim», `/tasdiqlash/` — admin tasdig'i.
- **Ta'mirlar:** `/tamirlar/` — ro'yxat va filtrlar (shu jumladan «Muddati o'tganlar»),
  `/navbat/` — ustalar uchun.
- **Hisobotlar:** `/hisobotlar/` — davr tanlanadi, Excel va PDF yuklab olinadi.
