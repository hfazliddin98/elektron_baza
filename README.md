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

# Ishga tushirish
python manage.py runserver
```

Sayt: http://127.0.0.1:8000/ · Admin panel: http://127.0.0.1:8000/admin/

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
