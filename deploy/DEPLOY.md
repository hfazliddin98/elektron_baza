# Serverga o'rnatish yo'riqnomasi

Ubuntu 22.04/24.04 uchun. Barcha buyruqlar `sudo` bilan bajariladi.
Loyiha `/srv/elektron_baza` papkasiga o'rnatiladi deb hisoblanadi.

---

## 1. Server tayyorlash

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip postgresql nginx git
sudo mkdir -p /var/log/elektron_baza
sudo chown www-data:www-data /var/log/elektron_baza
```

## 2. Ma'lumotlar bazasi

```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE elektron_baza;
CREATE USER baza_user WITH PASSWORD 'kuchli-parol-yozing';
ALTER ROLE baza_user SET client_encoding TO 'utf8';
ALTER ROLE baza_user SET timezone TO 'Asia/Tashkent';
GRANT ALL PRIVILEGES ON DATABASE elektron_baza TO baza_user;
\c elektron_baza
GRANT ALL ON SCHEMA public TO baza_user;
\q
```

## 3. Loyihani ko'chirish

```bash
cd /srv
sudo git clone https://github.com/hfazliddin98/elektron_baza.git
cd elektron_baza
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
```

## 4. Sozlamalar (`.env`)

```bash
sudo cp .env.example .env
sudo venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
sudo nano .env
```

`.env` da to'ldiring:

```ini
SECRET_KEY=<yuqoridagi buyruq bergan kalit>
DEBUG=False
ALLOWED_HOSTS=baza.universitet.uz
CSRF_TRUSTED_ORIGINS=https://baza.universitet.uz
HTTPS=True                    # ichki serverda sertifikat bo'lmasa: False

DB_NAME=elektron_baza
DB_USER=baza_user
DB_PASSWORD=<yuqorida qo'ygan parol>
DB_HOST=localhost
DB_PORT=5432

BOT_TOKEN=<BotFather bergan token>
BOT_ADMIN_CHAT=<operator/admin guruhining chat_id si>
SAYT_MANZILI=https://baza.universitet.uz
LOG_FAYL=/var/log/elektron_baza/app.log
```

> `.env` faylini hech qachon git'ga qo'shmang — unda parollar bor.

## 5. Baza va statik fayllar

```bash
cd /srv/elektron_baza
sudo venv/bin/python manage.py migrate
sudo venv/bin/python manage.py collectstatic --noinput
sudo venv/bin/python manage.py createsuperuser
sudo chown -R www-data:www-data /srv/elektron_baza
```

## 6. Gunicorn (sayt) va bot xizmatlari

```bash
sudo cp deploy/elektron-baza.service /etc/systemd/system/
sudo cp deploy/elektron-baza-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now elektron-baza
sudo systemctl enable --now elektron-baza-bot

sudo systemctl status elektron-baza
sudo systemctl status elektron-baza-bot
```

## 7. Nginx va HTTPS

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/elektron-baza
sudo nano /etc/nginx/sites-available/elektron-baza     # server_name ni o'zgartiring
sudo ln -s /etc/nginx/sites-available/elektron-baza /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# HTTPS sertifikat (internetga chiqadigan bo'lsa):
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d baza.universitet.uz
```

## 8. Zaxiralash va kunlik vazifalar

```bash
sudo cp deploy/backup.sh /usr/local/bin/elektron-baza-backup
sudo chmod +x /usr/local/bin/elektron-baza-backup
sudo /usr/local/bin/elektron-baza-backup          # qo'lda sinab ko'ring

sudo crontab deploy/crontab.txt
sudo crontab -l                                    # tekshirish
```

## 9. Boshlang'ich ma'lumotlar

1. Admin sifatida kiring: `https://baza.universitet.uz/admin/`
2. **Bo'limlarni** kiriting (yoki Excel importda avtomatik yaratiladi).
3. **Xodimlarni** Excel orqali yuklang: *Ma'lumotnoma → Xodimlarni import qilish*.
   Telefon raqamlarini to'g'ri yozing — bot shu raqam orqali taniydi.
4. **Qurilmalarni** Excel orqali yuklang: *Ma'lumotnoma → Qurilmalarni import qilish*.
5. **Ustalarni** admin panelda qo'shing va ularga foydalanuvchi (login) biriktiring.
6. Har bir xodim/usta uchun foydalanuvchi yarating va **rolini** to'g'ri belgilang.
7. **QR yorliqlarni** chop eting: *Ma'lumotnoma → QR yorliqlarni chop etish*
   → qurilmalarga yopishtiring.

## 10. Yangilanish (keyingi versiyalarni o'rnatish)

```bash
cd /srv/elektron_baza
sudo git pull
sudo venv/bin/pip install -r requirements.txt
sudo venv/bin/python manage.py migrate
sudo venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart elektron-baza elektron-baza-bot
```

---

## Muammolarni aniqlash

| Belgi | Tekshiring |
|-------|-----------|
| Sayt ochilmayapti (502) | `sudo systemctl status elektron-baza`, `sudo journalctl -u elektron-baza -n 50` |
| Statik fayllar (CSS) yo'q | `collectstatic` bajarilganmi, nginx'dagi `alias` yo'li to'g'rimi |
| Bot javob bermayapti | `sudo journalctl -u elektron-baza-bot -n 50`, `.env` dagi `BOT_TOKEN` |
| Telegram xabarlari kelmayapti | Xodimning `telegram_id` si bormi (u `/start` yuborganmi), `BOT_ADMIN_CHAT` to'g'rimi |
| Kunlik eslatmalar ishlamayapti | `sudo crontab -l`, `/var/log/elektron_baza/kunlik.log` |
| Zaxira yaratilmayapti | `/var/log/elektron_baza/backup.log`, `.env` dagi baza paroli |
| CSRF xatosi | `.env` dagi `CSRF_TRUSTED_ORIGINS` va `ALLOWED_HOSTS` |

Vaqti-vaqti bilan tekshirib turing:

```bash
cd /srv/elektron_baza
sudo venv/bin/python manage.py check --deploy     # xavfsizlik tavsiyalari
sudo venv/bin/python manage.py kunlik_vazifalar --quruq   # nima bo'lishini ko'rish
```
