#!/bin/bash
# Bazani va media fayllarni zaxiralaydi (kuniga bir marta cron orqali).
#
#   sudo cp deploy/backup.sh /usr/local/bin/elektron-baza-backup
#   sudo chmod +x /usr/local/bin/elektron-baza-backup
#
# Tekshirish: qo'lda bir marta ishga tushiring va fayl yaratilganini ko'ring.

set -euo pipefail

LOYIHA=/srv/elektron_baza
ZAXIRA=/var/backups/elektron_baza
SAQLASH_KUNI=30

# .env dan baza ma'lumotlarini o'qish
set -a
# shellcheck disable=SC1091
source "$LOYIHA/.env"
set +a

SANA=$(date +%Y%m%d_%H%M)
mkdir -p "$ZAXIRA"

# 1. Baza
PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h "${DB_HOST:-localhost}" -U "$DB_USER" -d "$DB_NAME" \
    | gzip > "$ZAXIRA/baza_$SANA.sql.gz"

# 2. Media fayllar (biriktirilgan rasmlar)
if [ -d "$LOYIHA/media" ]; then
    tar -czf "$ZAXIRA/media_$SANA.tar.gz" -C "$LOYIHA" media
fi

# 3. Eski zaxiralarni tozalash
find "$ZAXIRA" -name '*.gz' -mtime +$SAQLASH_KUNI -delete

echo "Zaxira tayyor: $ZAXIRA/baza_$SANA.sql.gz"

# Tiklash (kerak bo'lganda):
#   gunzip -c /var/backups/elektron_baza/baza_YYYYMMDD_HHMM.sql.gz \
#     | PGPASSWORD=... psql -h localhost -U USER -d DBNAME
