# Elektron Baza — Universitet qurilmalari ta'mirlash CRM tizimi

> **Loyiha maqsadi:** Universitetdagi elektron qurilmalarni (kompyuter, printer, proyektor va h.k.) ro'yxatga olish va ta'mirlash jarayonini boshqarish:
> - xodimlar ta'mirlash **murojaatlarini elektron yuboradi** — sayt sahifasi yoki **Telegram bot** orqali (shoshilinchlik darajasi bilan);
> - usta ishni **navbatdan o'zi tanlab oladi** (eng eski 10 ta ichidan) — majburiy biriktirish faqat shoshilinch holatlarda;
> - xodim istasa **ustani o'zi erkin tanlay oladi** (reytingi va ish yukini ko'rib) — tanlamasa umumiy navbat;
> - ta'mir tugagach xodim xizmatni **baholaydi** (sayt yoki bot orqali);
> - ba'zi qurilmalarni **xodim o'zi ta'mirlaydi** — hisobotini tizimga o'zi kiritadi, **admin tasdiqlaydi**;
> - muddat nazorati (**SLA**): har bosqichda kechikkan ta'mirlar avtomatik ko'rinadi;
> - kim ta'mirlagan, kim necha marta murojaat qilgan — **oylik/yillik hisobotlar** (Excel/PDF).
>
> **Stack:** Python (Django) + PostgreSQL + Bootstrap + aiogram (Telegram bot)
> **Umumiy muddat:** ~13–14 hafta · **MVP ~8-haftada real ishga tushadi**

---

## Umumiy jadval

| № | Bosqich | Muddat | Natija | Status |
|---|---------|--------|--------|--------|
| 1 | Tahlil va texnik topshiriq | 1 hafta | TZ hujjati | ⬜ Boshlanmagan |
| 2 | Loyihalash (ERD, arxitektura) | 1 hafta | Baza sxemasi, sahifa eskizlari | ⬜ Boshlanmagan |
| 3 | Muhitni tayyorlash | 2–3 kun | Django skelet loyiha | ✅ Tugagan |
| 4 | Modellar va admin panel | 1 hafta | Baza jadvallari, admin | ✅ Tugagan |
| 5 | Autentifikatsiya va rollar | 1 hafta | Login, 5 xil rol | ✅ Tugagan |
| 6 | Qurilmalar moduli | 1 hafta | Reestr + Excel import + QR-kod | ✅ Tugagan |
| 7 | Murojaatlar moduli | 1 hafta | Elektron murojaat + o'zi ta'mirlash + tasdiqlash | ✅ Tugagan |
| 8 | Ta'mirlash moduli | 2 hafta | Navbat, workflow, SLA | ✅ Tugagan |
| 🚀 | **MVP — birinchi ishga tushirish** | 8-bosqichdan keyin | Tizim real foydalanishda | 🟨 Sinovga tayyor |
| 9 | Baholash mexanizmi | 3–4 kun | 1–5 baho, ustalar reytingi | ✅ Tugagan |
| 10 | Telegram bot | 2 hafta | Bot: murojaat, xabarnoma, baho | ✅ Tugagan |
| 11 | Hisobotlar moduli | 1 hafta | Oylik/yillik hisobot, Excel/PDF | ✅ Tugagan |
| 12 | Testlash | 1 hafta | Barqaror versiya | ✅ Tugagan |
| 13 | Deploy va topshirish | 3–4 kun | Serverda ishlayotgan tizim + bot | 🟨 Fayllar tayyor |
| 14 | Qo'llab-quvvatlash | doimiy | Backup, yangilanishlar | 🟨 Yo'riqnoma tayyor |

Status belgilari: ⬜ Boshlanmagan · 🟨 Jarayonda · ✅ Tugagan

---

## 1-bosqich. Tahlil va texnik topshiriq (TZ)

**Maqsad:** tizimda nima saqlanishi va jarayonlar qanday borishini aniq yozib olish.

**Vazifalar:**
- [ ] Qurilma turlarini aniqlash (kompyuter, monitor, printer, proyektor, MFU va h.k.)
- [ ] Qurilma haqida saqlanadigan maydonlarni aniqlash (inventar raqam, model, seriya raqami, xona, bo'lim...)
- [ ] Murojaat jarayonini yozish: xodim yuboradi (sayt/bot) → operator ko'rib chiqadi → qabul/rad
- [ ] Ta'mirlash jarayoni qadamlarini yozish: qabul → navbat → tashxis → ta'mir → tayyor → topshirish → baholash
- [ ] **Navbat qoidasini tasdiqlash:** usta faqat navbatdagi **eng eski 10 ta** ta'mir ichidan tanlab oladi; operator faqat shoshilinchni to'g'ridan-to'g'ri biriktiradi
- [ ] **Usta tanlash qoidasi:** xodim murojaatda ustani ixtiyoriy tanlashi mumkin; tanlangan usta rad etsa yoki 1 ish kuni javob bermasa — ta'mir umumiy navbatga tushadi
- [ ] **Shoshilinchlik mezonlarini aniqlash:** qaysi holatlar "shoshilinch" hisoblanadi (masalan, dars xonasidagi proyektor)
- [ ] **SLA muddatlarini kelishish:** har status uchun ruxsat etilgan maksimal muddat (masalan, tashxis — 2 kun, ta'mir — 5 kun)
- [ ] **Qayta ta'mir oynasini kelishish:** topshirilgandan keyin necha kun ichida qaytsa "qayta ta'mir" hisoblanadi (taklif: 30 kun)
- [ ] O'zi ta'mirlash qoidalarini aniqlash: qaysi hollarda mumkin, hisobotda nima yoziladi, admin nimani tekshiradi
- [ ] Baholash qoidalari: 1–5 shkala, eslatma va avtoyopish muddatlari
- [ ] Foydalanuvchi rollarini aniqlash: **Admin**, **Operator**, **Usta**, **Xodim**, **Rahbariyat**
- [ ] Kerakli hisobotlar ro'yxatini tuzish (11-bosqichga qarang)
- [ ] `TZ.md` hujjatini yozib, tasdiqlatish

**Natija:** tasdiqlangan `TZ.md`.

**Tugash mezoni:** har bir jarayon qadami, muddatlar va har bir rol vazifasi aniq yozilgan.

---

## 2-bosqich. Loyihalash

**Maqsad:** kod yozishdan oldin baza sxemasi va sahifalarni chizib olish.

**Asosiy jadvallar (ERD):**

| Jadval | Asosiy maydonlar |
|--------|------------------|
| **Bolim** (kafedra/dekanat) | nomi, bino, xona |
| **Xodim** | user (FK — saytga kirish uchun), F.I.Sh., bo'lim (FK), lavozimi, telefon, **telegram_id** |
| **Qurilma** | inventar raqami (unikal), turi, modeli, seriya raqami, biriktirilgan bo'lim/xodim (FK), holati (ishlamoqda / ta'mirda / yaroqsiz), olingan sana, **QR-kod** |
| **Usta** | user (FK), F.I.Sh., mutaxassisligi, telefon |
| **TamirYozuvi** | qurilma (FK), xodim (FK), **turi** (usta ta'miri / o'zi ta'mirlagan), **manba** (operator / sayt / bot), **muhimlik** (oddiy / shoshilinch), muammo tavsifi, rasm, usta (FK, ixtiyoriy), **tanlangan usta** (FK — xodim o'zi so'ragan usta, ixtiyoriy), qabul/boshlangan/tugagan sanalar, bajarilgan ishlar, ehtiyot qismlar, xarajat, holat, **tasdiq holati** (o'zi ta'mirlaganlar uchun), **qayta ta'mir** (oldingi ta'mirga FK, avtomatik), **baho (1–5)**, baho izohi |
| **StatusTarix** | tamir_yozuvi (FK), eski holat, yangi holat, o'zgartirgan user (FK), sana — **SLA va bosqich muddatlari shu jadval asosida hisoblanadi** |

**Holatlar (status) oqimi:**
- Usta ta'miri: `Yangi murojaat → Qabul qilindi (navbat) → Tashxisda → Ta'mirda → Tayyor → Topshirildi` (+ `Rad etildi`)
- `Qabul qilindi` holatidagi yozuvlar umumiy **navbatni** tashkil qiladi — usta shu yerdan tanlab oladi
- Xodim ustani tanlagan bo'lsa: ta'mir o'sha ustaning shaxsiy ro'yxatiga tushadi; usta rad etsa (yoki 1 ish kuni javob bermasa) umumiy navbatga qaytadi
- O'zi ta'mirlagan: `Tasdiq kutilmoqda → Tasdiqlandi / Rad etildi`

**Vazifalar:**
- [ ] ERD diagrammani chizish (jadvallar va bog'lanishlar)
- [ ] Status oqimlarini tasdiqlash (yuqoridagi ikkala yo'l)
- [ ] Django app strukturasini belgilash: `accounts`, `devices`, `repairs`, `reports`, `bot`
- [ ] Asosiy sahifalar eskizini chizish: dashboard, qurilmalar, murojaat yuborish, murojaatlar navbati, ustalar navbat sahifasi, ta'mirlar, tasdiqlash navbati, hisobotlar
- [ ] Bot dialoglari ssenariysini yozish (qadam-baqadam xabarlar)

**Natija:** ERD diagramma + sahifalar ro'yxati + bot ssenariysi.

**Tugash mezoni:** har bir jadvalning barcha maydonlari va bog'lanishlari aniq.

---

## 3-bosqich. Muhitni tayyorlash

**Maqsad:** ishlab chiqish muhitini sozlash.

**Vazifalar:**
- [x] `.gitignore`, `README.md` yaratish
- [x] Virtual muhit: `python -m venv venv`, `requirements.txt`
- [x] Django loyihasini yaratish: `django-admin startproject config .`
- [x] Applarni yaratish: `accounts`, `devices`, `repairs`, `reports`, `bot`
- [x] PostgreSQL ulanishi sozlandi — `.env` da `DB_NAME` to'ldirilsa PostgreSQL, bo'sh qolsa SQLite (bot tokeni ham `.env` da)
- [x] Bootstrap shablonini ulash (base.html, navbar)
- [x] Birinchi commit va GitHub'ga push

**Natija:** `runserver` bilan ishga tushadigan skelet loyiha.

**Tugash mezoni:** loyiha klonlanib 5 daqiqada ishga tushadi.

---

## 4-bosqich. Modellar va admin panel

**Maqsad:** ERD asosida haqiqiy baza jadvallarini yaratish.

**Vazifalar:**
- [x] Maxsus `User` modeli (`accounts` app) — `rol` maydoni bilan (admin/operator/usta/xodim/rahbariyat), `AUTH_USER_MODEL` sozlandi
- [x] `Bolim`, `Xodim` modellari (`devices` app) — Xodim User bilan bog'lanadi, `telegram_id` maydoni bilan
- [x] `Qurilma` modeli — inventar raqami unikal
- [x] `Usta` modeli (`accounts` app, User bilan bog'langan)
- [x] `TamirYozuvi` modeli — `turi`, `manba`, `muhimlik`, `holat`, `tasdiq holati`, `baho` uchun `choices`; `qayta_tamir` FK; sanalar avtomatik; qurilma holati avtomatik sinxronlanadi; qayta ta'mir (30 kun) avtomatik aniqlanadi
- [x] `StatusTarix` modeli — har status o'zgarishida avtomatik yoziladi (save metodi orqali)
- [x] Migratsiyalar: `makemigrations` + `migrate`
- [x] Barcha modellarni admin panelda ro'yxatdan o'tkazish (qidiruv, filtr, autocomplete, status tarixi inline bilan)
- [x] Test uchun namunaviy ma'lumotlar — `python manage.py namuna` (3 bo'lim, 6 xodim, 4 usta, 12 qurilma, 5 ta'mir yozuvi)

**Natija:** to'liq baza + ishlaydigan admin panel.

**Tugash mezoni:** admin panel orqali qurilma qo'shib, unga har ikki turdagi ta'mir yozuvi ochish mumkin; status o'zgarishi tarixga tushadi.

---

## 5-bosqich. Autentifikatsiya va rollar

**Maqsad:** har bir foydalanuvchi faqat o'z vazifasiga mos sahifalarni ko'rishi.

**Rollar va huquqlar:**

| Rol | Huquqlar |
|-----|----------|
| **Admin** | hamma narsa + o'zi-ta'mir hisobotlarini **tasdiqlash** |
| **Operator** | murojaatlarni ko'rib chiqish (qabul/rad), **shoshilinch** ta'mirni ustaga biriktirish, qurilma topshirish |
| **Usta** | **navbatdagi eng eski 10 ta ichidan ta'mirni o'ziga olish**, unga shaxsan so'ralgan ta'mirni qabul qilish / rad etish, o'z ta'mirlarida status va bajarilgan ishlarni yozish |
| **Xodim** | murojaat yuborish (istasa **ustani o'zi tanlab**), o'z murojaatlari holatini kuzatish, xizmatni baholash, o'zi ta'mirlaganini kiritish |
| **Rahbariyat** | faqat hisobotlarni ko'rish |

**Vazifalar:**
- [x] Login / logout sahifalari (Bootstrap dizayn bilan)
- [x] Rollar: `accounts.User.rol` maydoni asosida ruxsatlar ulandi
- [x] Har bir view'da rol tekshiruvi — `accounts/permissions.py`: `@rol_kerak(ADMIN, OPERATOR)` dekoratori va `RolTalabMixin`; superuser hamma joyga kiradi; ruxsatsiz urinish tarixga yoziladi
- [x] Parolni o'zgartirish sahifasi
- [x] Har bir amal tarixini saqlash — `AmalTarixi` modeli + `amal_yoz()` yordamchisi; kirish/chiqish/xato parol signal orqali avtomatik yoziladi
- [x] Rolga qarab o'zgaradigan panel (dashboard) va navbar
- [x] Admin uchun amallar tarixi sahifasi (qidiruv, filtr, sahifalash)
- [x] Testlar: 10 ta test (rollar, kirish/chiqish, parol, audit log) — hammasi o'tadi

**Natija:** 5 rolli kirish tizimi.

**Tugash mezoni:** har bir rol faqat o'z sahifalarini ko'radi; xodim boshqa xodimning murojaatini ko'ra olmaydi.

> **Eslatma:** murojaat/ta'mir sahifalari qurilganda (7–8-bosqich) har bir view'ga `@rol_kerak(...)`
> qo'yish va muhim amallardan keyin `amal_yoz(...)` chaqirish kerak.

---

## 6-bosqich. Qurilmalar moduli

**Maqsad:** universitetdagi barcha elektron qurilmalarni ro'yxatga olish.

**Vazifalar:**
- [x] Qurilmalar ro'yxati: jadval ko'rinishida, sahifalash bilan (25 tadan)
- [x] Filtr: turi, bo'limi, holati bo'yicha; inventar raqam / model / seriya raqami bo'yicha qidiruv
- [x] Yangi qurilma qo'shish formasi (validatsiya bilan)
- [x] **Excel'dan ommaviy import:** qurilmalar va xodimlar uchun alohida shablon (yuklab olish tugmasi bilan); bo'limlar avtomatik yaratiladi va hisobotda ko'rsatiladi; qayta yuklashga chidamli (mavjudlar o'tkazib yuboriladi yoki «yangilash» belgilansa yangilanadi)
- [x] Import xatolarini tushunarli ko'rsatish — har xato qator raqami va sababi bilan; ogohlantirishlar alohida (masalan, topilmagan xodim)
- [x] **QR-kod:** har qurilma uchun QR (`/qurilmalar/<id>/qr.png`), qurilma sahifasida ko'rinadi; filtrlangan yorliqlarni chop etish sahifasi (`@media print` bilan)
- [x] Qurilma sahifasi: ma'lumotlari + **barcha ta'mir tarixi** (usta ta'mirlari ham, o'zi ta'mirlanganlari ham, qayta ta'mir belgisi bilan)
- [x] Tahrirlash / yaroqsizga chiqarish (o'chirmasdan, tasdiqlash oynasi bilan)
- [x] Bo'limlar va xodimlar uchun CRUD sahifalari
- [x] Rollar: xodim faqat o'ziga va o'z bo'limiga tegishli qurilmalarni ko'radi; rahbariyat reestrga kirmaydi; import faqat admin uchun
- [x] Testlar: 20 ta test (ruxsatlar, CRUD, QR, Excel import va xatolari)

**Natija:** qurilmalar reestri (import va QR bilan).

**Tugash mezoni:** Excel'dagi mavjud ro'yxat 10 daqiqada tizimga yuklanadi; har qurilmaning QR-kodini chop etish mumkin.

> **Eslatma:** QR skanerlanganda hozircha qurilma sahifasi ochiladi. Murojaat formasi
> 7-bosqichda qurilgach, shu sahifaga «Ta'mirga murojaat yuborish» tugmasi qo'shiladi.

---

## 7-bosqich. Murojaatlar moduli (elektron qabul + o'zi ta'mirlash)

**Maqsad:** xodimlar murojaatni tizim orqali yuborishi, o'zi ta'mirlaganini esa hisobot qilib kiritishi.

**Vazifalar — elektron murojaat:**
- [x] Xodim kabineti: "Murojaat yuborish" formasi (o'z bo'limi qurilmasini tanlaydi, muammo tavsifi, rasm biriktirish)
- [x] Formada **shoshilinchlik tanlovi** (oddiy / shoshilinch)
- [x] **Ixtiyoriy usta tanlash:** «Farqi yo'q» varianti bilan; tanlanmasa umumiy navbat
- [x] "Mening murojaatlarim" sahifasi — har bir murojaat holatini kuzatish
- [x] Operator sahifasi: yangi murojaatlar navbati (shoshilinchlar tepada), qabul qilish / rad etish (rad sababi majburiy)
- [x] Qabul qilinganda murojaat ta'mir navbatiga tushishi
- [x] QR skanerlanganda qurilma sahifasidan to'g'ridan-to'g'ri murojaat yuborish tugmasi

**Vazifalar — o'zi ta'mirlash:**
- [x] "O'zim ta'mirladim" formasi: qurilma, nima buzilgan edi, nima qilindi, ehtiyot qism, xarajat
- [x] Yuborilganda holat: `Tasdiq kutilmoqda`
- [x] Admin tasdiqlash navbati sahifasi: ko'rib chiqish → **tasdiqlash / rad etish** (rad etilsa izoh majburiy)
- [x] Tasdiqlangan yozuv qurilma tarixiga va hisobotlarga kirishi; rad etilgani hisobotlarga kirmasligi (`hisobga_kiradi()` filtri)

**Natija:** elektron murojaat qabul tizimi + tasdiqlanadigan o'zi-ta'mir hisobotlari.

**Tugash mezoni:** xodim saytdan murojaat yuborib holatini kuzata oladi; o'zi ta'mirlagani admin tasdig'idan keyingina tarixga tushadi.

---

## 8-bosqich. Ta'mirlash moduli (asosiy modul)

**Maqsad:** ta'mirlash jarayonini navbat va muddat nazorati bilan tizimda yuritish.

**Jarayon (workflow):**

```
  Xodim murojaat yuboradi                  Xodim qurilmani o'zi ta'mirlaydi
  (sayt / bot / operator orqali)                       ↓
        ↓                                   Hisobot kiritadi → "Tasdiq kutilmoqda"
   "Yangi murojaat"                                    ↓
        ↓                                   Admin: tasdiqlaydi / rad etadi
  Operator ko'rib chiqadi (qabul / rad)                ↓
        ↓                                   Tarix va hisobotlarga qo'shiladi
   "Qabul qilindi"
        ↓
  Xodim usta tanlaganmi?
   ├─ HA → o'sha ustaning shaxsiy ro'yxatiga tushadi
   │       (usta rad etsa yoki 1 ish kuni javob
   │        bermasa → umumiy navbatga qaytadi)
   └─ YO'Q → NAVBATGA tushadi —
             usta navbatdan O'ZI tanlab oladi
             (eng eski 10 ta ichidan, shoshilinchlar
              tepada; shoshilinchni operator
              to'g'ridan-to'g'ri biriktirishi ham mumkin)
        ↓
   "Tashxisda" → "Ta'mirda" → "Tayyor"
        ↓
   "Topshirildi"  (botga xabar boradi)
        ↓
  Xodim baholaydi (1–5) — 3 kunda eslatma,
  7 kunda bahosiz avto-yopiladi
```

**Vazifalar:**
- [x] Operator uchun to'g'ridan-to'g'ri qabul formasi (xodim qurilmani o'zi olib kelgan holat uchun) — darhol navbatga tushadi
- [x] **Ustalar uchun "Navbat" sahifasi:** `Qabul qilindi` holatidagi **eng eski 10 ta** ta'mir (shoshilinchlar tepada), "O'zimga olish" tugmasi
- [x] Bir ta'mirni faqat bitta usta olishi — `select_for_update` bilan tranzaksiya ichida tekshiriladi (test bilan qamralgan)
- [x] **"Sizdan so'ralgan ishlar" bo'limi:** qabul qilish / rad etish tugmalari; rad etilsa yoki 1 ish kuni javob berilmasa umumiy navbatga tushadi (kunlik buyruq ham, navbat so'rovi ham shu qoidaga bo'ysunadi)
- [x] Operator **shoshilinch** ta'mirni to'g'ridan-to'g'ri biriktira olishi
- [x] Status o'zgartirish tugmalari rol va holatga qarab ko'rinadi; har o'zgarish `StatusTarix`ga yoziladi
- [x] **SLA nazorati:** har holat uchun muddat (`SLA_KUN`), muddati o'tganlar qizil belgi bilan; ro'yxatda «Muddati o'tganlar» filtri; adminga kunlik Telegram eslatmasi
- [x] **Qayta ta'mir:** 30 kun ichida qaytgan qurilma avtomatik belgilanadi va oldingi ta'mirga bog'lanadi
- [x] Ta'mir boshlanganda qurilma holati avtomatik "ta'mirda", topshirilganda "ishlamoqda"
- [x] Ustaning shaxsiy sahifasi: "Mening ta'mirlarim"
- [x] Dashboard: yangi murojaatlar, navbatda, ta'mirda, tayyor, tasdiq kutayotgan, **muddati o'tgan (SLA)** soni

**Natija:** navbat va SLA nazorati bilan to'liq ishlaydigan ta'mirlash jarayoni.

**Tugash mezoni:** murojaatdan topshirishgacha butun jarayon tizimda o'tadi; usta ishni navbatdan o'zi oladi; kechikkan ta'mir dashboardda qizil ko'rinadi.

---

## 🚀 MVP — birinchi ishga tushirish (8-bosqichdan keyin)

**Maqsad:** tizim to'liq tugashini kutmasdan, ishlaydigan qismini real foydalanishga qo'yish. Real foydalanish rejada ko'rinmagan muammolarni erta ochadi — bot va baholash tayyor jarayon ustiga quriladi.

**MVP tarkibi:** qurilmalar reestri (Excel import + QR), saytdan murojaat, navbat va ta'mir jarayoni, soddalashtirilgan oylik hisobot.

**Vazifalar:**
- [ ] Soddalashtirilgan oylik hisobot sahifasi (to'liq modul 11-bosqichda bo'ladi)
- [ ] Universitet ichki serveriga (yoki bitta kompyuterga) vaqtinchalik joylash
- [ ] Operator va 1–2 usta bilan **1 haftalik sinov**
- [ ] Fikr-mulohazalarni yig'ish, ro'yxat qilish va keyingi bosqichlarda tuzatish sifatida kiritish

**Tugash mezoni:** kamida 10 ta real ta'mir tizim orqali boshdan-oxir o'tgan.

---

## 9-bosqich. Baholash mexanizmi

**Maqsad:** xodim ta'mir sifatini baholashi, ustalar reytingi shakllanishi.

**Vazifalar:**
- [x] Qurilma "Topshirildi" bo'lgach xodimga baholash imkoniyati ochilishi (1–5 + ixtiyoriy izoh)
- [x] Baho faqat o'z murojaatiga va faqat bir marta berilishi
- [x] Saytda: ta'mir sahifasida baholash tugmasi (modal oyna)
- [x] **3 kun ichida baho qo'yilmasa** — bot orqali bir marta eslatma (`kunlik_vazifalar`)
- [x] **7 kundan keyin** bahosiz avtomatik yopilishi (`baho_yopilgan`, hisobotda "baholanmagan")
- [x] Usta panelida o'rtacha reyting ko'rinishi
- [x] Past baho (1–2) qo'yilsa adminlarga Telegram bildirishnomasi
- [x] Baholar hisobotlarga ulanishi (11-bosqich)

**Natija:** ishlaydigan baholash tizimi va ustalar reytingi.

**Tugash mezoni:** topshirilgan har bir ta'mirni xodim baholay oladi; usta reytingi avtomatik hisoblanadi; baholanmaganlar 7 kunda avto-yopiladi.

---

## 10-bosqich. Telegram bot

**Maqsad:** murojaat yuborish, xabarnoma olish va baholashni Telegram orqali ham qilish.

**Vazifalar:**
- [x] Bot yaratish (aiogram 3), token `.env` da; `python manage.py bot` bilan ishga tushadi
- [x] Ro'yxatdan o'tish: telefon raqami orqali xodim yoki usta profiliga bog'lanadi (`telegram_id`); bitta Telegram hisobi faqat bitta profilga bog'lanadi
- [x] Murojaat yuborish: qurilma → muammo → **shoshilinchlik** → **usta tanlash** («Farqi yo'q» tugmasi bilan)
- [x] "Mening murojaatlarim" — bot orqali holatlarni ko'rish; baholanmaganlar uchun baho tugmalari
- [x] Ustalar uchun: «Navbat» va «Mening ishlarim» bo'limlari
- [x] Xodimga avtomatik xabarnomalar: qabul qilindi, ta'mirga olindi, qurilmangiz tayyor, topshirildi, rad etildi
- [x] **Ustalarga xabarnomalar:** navbatga yangi ish (shoshilinch alohida belgi bilan), shaxsan so'ralganda, biriktirilganda
- [x] Topshirilgandan keyin bot baholash so'rashi (1–5 tugmalar)
- [x] **Baho eslatmasi:** 3 kundan keyin (`kunlik_vazifalar`)
- [x] Operator/admin guruhiga yangi murojaat, past baho va SLA ogohlantirishlari
- [x] Django bilan umumiy baza orqali integratsiya (polling; xabar yuborish `urllib` orqali — bot jarayoni ishlamasa ham xabarlar boradi)

**Natija:** to'liq ishlaydigan Telegram bot.

**Tugash mezoni:** xodim botdan murojaat yuborib, "tayyor" xabarini olib, botdan baho qo'ya oladi; ustalar yangi ishdan xabardor bo'ladi.

> **Eslatma:** botni ishga tushirish uchun `.env` da `BOT_TOKEN` bo'lishi kerak.
> Token bo'lmasa sayt xatosiz ishlayveradi — xabarlar shunchaki yuborilmaydi.

---

## 11-bosqich. Hisobotlar moduli

**Maqsad:** rahbariyat uchun oylik va yillik hisobotlar.

**Hisobot turlari:**
- [x] **Oylik/yillik umumiy hisobot:** kelib tushgan, tugatilgan, rad etilgan, jarayondagi, o'rtacha ta'mir muddati
- [x] **Bosqichlar bo'yicha o'rtacha vaqt:** qabuldan navbatgacha, navbatda kutish, ta'mir ishlari, topshirishgacha
- [x] **Ustalar kesimida:** ta'mirlar soni + **o'rtacha baho (reyting)** + **qayta ta'mirlar foizi** + **shaxsan so'ralgan soni** + hozirgi ish yuki
- [x] **SLA buzilishlari:** muddati o'tgan ta'mirlar ro'yxati va kechikish kunlari
- [x] **Xodimlar kesimida:** kim necha marta murojaat qilgan
- [x] **O'zi ta'mirlanganlar:** xodim kesimida (faqat tasdiqlanganlari)
- [x] **Bo'limlar kesimida:** qurilmalar va murojaatlar soni
- [x] **Qurilmalar kesimida:** eng ko'p ta'mirlangan 15 ta qurilma va ularga ketgan xarajat
- [x] **Murojaat manbalari:** sayt / bot / operator nisbati (diagramma)
- [x] **Xarajatlar:** davr bo'yicha jami (tasdiqlanmagan o'zi-ta'mirlar hisobga kirmaydi)

**Vazifalar:**
- [x] Davr tanlash: sana oralig'i + tayyor tugmalar (shu oy, o'tgan oy, shu yil, o'tgan yil)
- [x] Diagrammalar (Chart.js): oylik dinamika, ustalar taqqoslash + reyting, manbalar
- [x] **Excel'ga eksport** (openpyxl) — 6 varaqli fayl
- [x] **PDF hisobot** (xhtml2pdf — WeasyPrint o'rniga, chunki Windows'da qo'shimcha kutubxonasiz ishlaydi)
- [x] Rahbariyat roli uchun hisobotlar bo'limi (boshqa bo'limlarga kirmaydi)
- [x] Barcha uch format bitta hisoblash moduli (`reports/hisobot.py`) dan foydalanadi — raqamlar bir xil bo'lishi kafolatlanadi

**Natija:** oylik/yillik hisobotlar tizimi.

**Tugash mezoni:** "2026 yil iyun oyida kim nechta qurilma ta'mirlagan, reytingi va qayta ta'mir foizi qancha" savoliga 2 ta klik bilan Excel fayl olish mumkin.

---

## 12-bosqich. Testlash

**Maqsad:** real ishga tushirishdan oldin xatolardan tozalash.

**Vazifalar:**
- [x] Modellar va view'lar uchun testlar — **jami 91 ta test**, `python manage.py test` bilan ishga tushadi
- [x] **To'liq zanjir testi** (`repairs/tests_integratsiya.py`): saytdan murojaat → qabul → navbat → ta'mir → topshirish → baho → hisobot; va botdan murojaat → baho → hisobot
- [x] **Navbat tekshiruvi:** ikki usta bir ishni olishga urinsa faqat bittasiga tegishi; navbat tartibi (shoshilinch tepada)
- [x] **Usta tanlash tekshiruvi:** rad etilganda va 1 ish kuni javob bo'lmaganda umumiy navbatga qaytishi
- [x] O'zi-ta'mir oqimi: tasdiqlangani hisobotga tushishi, rad etilgani tushmasligi
- [x] **Excel import:** noto'g'ri sarlavha, xato qatorlar (qator raqami bilan), takroriy inventar raqam, mavjudlarni o'tkazib yuborish/yangilash
- [x] **SLA va qayta ta'mir:** kechikkanlar aniqlanishi, 30 kun ichida qaytgan qurilma belgilanishi, 40 kundan keyingisi belgilanmasligi
- [x] **Avtoyopish:** 3 kunda eslatma, 7 kunda bahosiz yopilish, `--quruq` rejim hech narsani o'zgartirmasligi
- [x] Rollar tekshiruvi: har bir rol uchun ruxsat etilgan/etilmagan sahifalar (403)
- [x] Baho faqat bir marta va faqat o'z murojaatiga qo'yilishi
- [x] Bot: telefon formatlarini tanish, profil bog'lash, murojaat yaratish, baho, Telegram ishlamaganda dastur yiqilmasligi
- [x] Hisobot raqamlari (xarajat, reyting, qayta ta'mir foizi) test bilan tekshirilgan
- [x] Topilgan xatolar tuzatildi (masalan: bitta Telegram hisobi ikkala profilga bog'lanib qolishi, xodim ko'ra olmaydigan qurilma QR-kodini olishi)

**Natija:** barqaror versiya.

**Tugash mezoni:** kritik xatolar yo'q, hisobot raqamlari aniq, bot barqaror ishlaydi.

> **Qolgan qo'lda tekshiruv:** haqiqiy Telegram boti bilan (token bilan) dialoglarni
> bir marta o'tib chiqish va real foydalanuvchilar bilan 1 haftalik sinov (MVP bosqichi).

---

## 13-bosqich. Deploy va topshirish

**Maqsad:** tizimni universitet serveriga joylash.

**Tayyor fayllar** (`deploy/` papkasi):
- [x] `DEPLOY.md` — qadam-baqadam o'rnatish yo'riqnomasi (server, PostgreSQL, `.env`, xizmatlar, HTTPS, muammolarni aniqlash jadvali)
- [x] `elektron-baza.service` — Gunicorn uchun systemd xizmati
- [x] `elektron-baza-bot.service` — bot uchun systemd xizmati (avtomatik qayta ishga tushadi)
- [x] `nginx.conf` — static/media yo'llari va proksi sozlamalari bilan
- [x] `backup.sh` — kunlik baza va media zaxirasi, 30 kundan eskisini tozalash, tiklash buyrug'i izohda
- [x] `crontab.txt` — `kunlik_vazifalar`, zaxiralash va sessiyalarni tozalash jadvali
- [x] Production xavfsizlik sozlamalari `settings.py` da (`DEBUG=False` bo'lganda HTTPS, HSTS, xavfsiz cookie'lar; ichki server uchun `HTTPS=False` varianti)
- [x] Fayl loglari (`LOG_FAYL`) va aylanuvchi log fayllari
- [x] `QOLLANMA.md` — foydalanuvchi qo'llanmasi (xodim, usta, operator, admin, rahbariyat bo'limlari + tez-tez so'raladigan savollar)

**Serverda bajariladigan ishlar** (universitet serveri kerak):
- [ ] Serverni tayyorlash va `DEPLOY.md` bo'yicha o'rnatish
- [ ] Real ma'lumotlarni kiritish — Excel import orqali (qurilmalar, xodimlar)
- [ ] QR-kodlarni chop etib qurilmalarga yopishtirish
- [ ] BotFather'dan token olib `.env` ga yozish, operator/admin guruhini yaratish
- [ ] Foydalanuvchilarni o'qitish (`QOLLANMA.md` asosida)

**Tugash mezoni:** xodimlar saytdan/botdan murojaat yuborib ishlay oladi; QR-kodlar qurilmalarga yopishtirilgan.

---

## 14-bosqich. Qo'llab-quvvatlash va rivojlantirish

**Doimiy vazifalar:**
- [ ] Backuplar ishlashini muntazam tekshirish (`/var/log/elektron_baza/backup.log`)
- [ ] Foydalanuvchi muammolarini tuzatish
- [ ] Kutubxonalarni yangilab borish (`pip list --outdated`)
- [ ] Har chorakda hisobotlarni ko'rib chiqish: eng ko'p ta'mirlangan qurilmalarni almashtirish rejasi

**Muntazam tekshiruv ro'yxati** (oyiga bir marta):

| Tekshiruv | Buyruq / joy |
|-----------|--------------|
| Zaxira yaratilyaptimi | `ls -lh /var/backups/elektron_baza \| tail` |
| Xizmatlar ishlayaptimi | `systemctl status elektron-baza elektron-baza-bot` |
| Kunlik vazifalar bajarilyaptimi | `tail /var/log/elektron_baza/kunlik.log` |
| Xavfsizlik ogohlantirishlari | `venv/bin/python manage.py check --deploy` |
| Testlar o'tyaptimi (yangilanishdan keyin) | `venv/bin/python manage.py test` |
| Muddati o'tgan ta'mirlar ko'p emasmi | Panel → «Muddati o'tgan (SLA)» |

**Kelajakdagi g'oyalar:**
- [ ] REST API (Django REST Framework) — mobil ilova uchun
- [ ] Ehtiyot qismlar ombori moduli
- [ ] SMS xabarnomalar (Telegram ishlatmaydigan xodimlar uchun)
- [ ] Botdan turib usta ishni qabul qilishi (hozir sayt orqali)

---

*Oxirgi yangilanish: 2026-07-23*
