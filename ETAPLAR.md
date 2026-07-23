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
| 4 | Modellar va admin panel | 1 hafta | Baza jadvallari, admin | ⬜ Boshlanmagan |
| 5 | Autentifikatsiya va rollar | 1 hafta | Login, 5 xil rol | ⬜ Boshlanmagan |
| 6 | Qurilmalar moduli | 1 hafta | Reestr + Excel import + QR-kod | ⬜ Boshlanmagan |
| 7 | Murojaatlar moduli | 1 hafta | Elektron murojaat + o'zi ta'mirlash + tasdiqlash | ⬜ Boshlanmagan |
| 8 | Ta'mirlash moduli | 2 hafta | Navbat, workflow, SLA | ⬜ Boshlanmagan |
| 🚀 | **MVP — birinchi ishga tushirish** | 8-bosqichdan keyin | Tizim real foydalanishda | ⬜ Boshlanmagan |
| 9 | Baholash mexanizmi | 3–4 kun | 1–5 baho, ustalar reytingi | ⬜ Boshlanmagan |
| 10 | Telegram bot | 2 hafta | Bot: murojaat, xabarnoma, baho | ⬜ Boshlanmagan |
| 11 | Hisobotlar moduli | 1 hafta | Oylik/yillik hisobot, Excel/PDF | ⬜ Boshlanmagan |
| 12 | Testlash | 1 hafta | Barqaror versiya | ⬜ Boshlanmagan |
| 13 | Deploy va topshirish | 3–4 kun | Serverda ishlayotgan tizim + bot | ⬜ Boshlanmagan |
| 14 | Qo'llab-quvvatlash | doimiy | Backup, yangilanishlar | ⬜ Boshlanmagan |

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
- [ ] `Bolim`, `Xodim` modellari (`devices` app) — Xodim User bilan bog'lanadi, `telegram_id` maydoni bilan
- [ ] `Qurilma` modeli — inventar raqami unikal
- [ ] `Usta` modeli (`accounts` app, User bilan bog'langan)
- [ ] `TamirYozuvi` modeli — `turi`, `manba`, `muhimlik`, `holat`, `tasdiq holati`, `baho` uchun `choices`; `qayta_tamir` FK; sanalar avtomatik
- [ ] `StatusTarix` modeli — har status o'zgarishida avtomatik yozilishi (save metodi yoki signal orqali)
- [ ] Migratsiyalar: `makemigrations` + `migrate`
- [ ] Barcha modellarni admin panelda ro'yxatdan o'tkazish (qidiruv, filtr bilan)
- [ ] Test uchun namunaviy ma'lumotlar (10–15 ta qurilma, 3–4 usta, 5–6 xodim)

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
- [ ] Login / logout sahifalari
- [ ] Rollarni Django groups yoki `role` maydoni orqali qilish
- [ ] Har bir view'da rol tekshiruvi (decorator/mixin)
- [ ] Parolni o'zgartirish
- [ ] Har bir amal tarixini saqlash (kim, qachon, nima qildi)

**Natija:** 5 rolli kirish tizimi.

**Tugash mezoni:** har bir rol faqat o'z sahifalarini ko'radi; xodim boshqa xodimning murojaatini ko'ra olmaydi.

---

## 6-bosqich. Qurilmalar moduli

**Maqsad:** universitetdagi barcha elektron qurilmalarni ro'yxatga olish.

**Vazifalar:**
- [ ] Qurilmalar ro'yxati: jadval ko'rinishida, sahifalash bilan
- [ ] Filtr: turi, bo'limi, holati bo'yicha; inventar raqam bo'yicha qidiruv
- [ ] Yangi qurilma qo'shish formasi (validatsiya bilan)
- [ ] **Excel'dan ommaviy import:** qurilmalar va xodimlar ro'yxatini tayyor shablon orqali yuklash (openpyxl) — yuzlab yozuvni qo'lda kiritmaslik uchun
- [ ] Import xatolarini tushunarli ko'rsatish (qaysi qator, nima sabab)
- [ ] **QR-kod:** har qurilma uchun avtomatik QR generatsiya (`qrcode` kutubxonasi), chop etish uchun ko'rinish; skanerlashda qurilma sahifasi va tayyor murojaat formasi ochiladi
- [ ] Qurilma sahifasi: ma'lumotlari + **barcha ta'mir tarixi** (usta ta'mirlari ham, o'zi ta'mirlanganlari ham)
- [ ] Tahrirlash / yaroqsizga chiqarish (o'chirmasdan, holatini o'zgartirish)
- [ ] Bo'limlar va xodimlar uchun CRUD sahifalari

**Natija:** qurilmalar reestri (import va QR bilan).

**Tugash mezoni:** Excel'dagi mavjud ro'yxat 10 daqiqada tizimga yuklanadi; har qurilmaning QR-kodini chop etish mumkin.

---

## 7-bosqich. Murojaatlar moduli (elektron qabul + o'zi ta'mirlash)

**Maqsad:** xodimlar murojaatni tizim orqali yuborishi, o'zi ta'mirlaganini esa hisobot qilib kiritishi.

**Vazifalar — elektron murojaat:**
- [ ] Xodim kabineti: "Murojaat yuborish" formasi (o'ziga biriktirilgan qurilmani tanlaydi, muammo tavsifi, rasm biriktirish)
- [ ] Formada **shoshilinchlik tanlovi** (oddiy / shoshilinch)
- [ ] **Ixtiyoriy usta tanlash:** xodim xohlasa ro'yxatdan ustani tanlaydi (har ustaning reytingi va hozirgi ish yuki ko'rinib turadi); tanlamasa — umumiy navbat
- [ ] "Mening murojaatlarim" sahifasi — har bir murojaat holatini kuzatish
- [ ] Operator sahifasi: yangi murojaatlar navbati (shoshilinchlar tepada), qabul qilish / rad etish (rad sababi bilan)
- [ ] Qabul qilinganda murojaat ta'mir navbatiga tushishi (8-bosqich bilan bog'lanadi)

**Vazifalar — o'zi ta'mirlash:**
- [ ] "O'zim ta'mirladim" formasi: qurilma, nima buzilgan edi, nima qilindi, ehtiyot qism, xarajat
- [ ] Yuborilganda holat: `Tasdiq kutilmoqda`
- [ ] Admin tasdiqlash navbati sahifasi: ko'rib chiqish → **tasdiqlash / rad etish** (izoh bilan)
- [ ] Tasdiqlangan yozuv qurilma tarixiga va hisobotlarga kirishi; rad etilgani sabab bilan xodimga ko'rinishi

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
- [ ] Operator uchun to'g'ridan-to'g'ri qabul formasi ham (xodim qurilmani o'zi olib kelgan holat uchun)
- [ ] **Ustalar uchun "Navbat" sahifasi:** `Qabul qilindi` holatidagi **eng eski 10 ta** ta'mir ko'rinadi (shoshilinchlar tepada), "O'zimga olish" tugmasi
- [ ] Bir ta'mirni faqat bitta usta olishi — ikki usta bir vaqtda bossa, birinchisiniki o'tadi (poyga holati tekshiruvi)
- [ ] **"Menga so'ralgan ta'mirlar" bo'limi:** xodim shaxsan tanlagan ta'mirlar ustaning sahifasida alohida ko'rinadi — qabul qilish / rad etish tugmalari; rad etilsa yoki 1 ish kuni javob berilmasa avtomatik umumiy navbatga tushadi
- [ ] Operator **shoshilinch** ta'mirni to'g'ridan-to'g'ri biriktira olishi; biriktirish oynasida **har ustaning hozirgi aktiv ta'mirlari soni** ko'rinishi (ish yuki)
- [ ] Status o'zgartirish tugmalari (har rol o'ziga ruxsat berilganini); har o'zgarish `StatusTarix`ga yozilishi
- [ ] **SLA nazorati:** statusda ruxsat etilgan muddatdan oshgan ta'mirlar ro'yxatda **qizil** ko'rinishi; adminga kunlik eslatma
- [ ] **Qayta ta'mir:** topshirilgandan 30 kun ichida o'sha qurilma yana kelsa — avtomatik "qayta ta'mir" belgisi, oldingi ta'mirga bog'lanadi
- [ ] Ta'mir boshlanganda qurilma holati avtomatik "ta'mirda", topshirilganda "ishlamoqda"
- [ ] Ustaning shaxsiy sahifasi: "Mening ta'mirlarim"
- [ ] Dashboard: yangi murojaatlar, navbatda, ta'mirda, tayyor, tasdiq kutayotgan, **muddati o'tgan (SLA)** soni

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
- [ ] Qurilma "Topshirildi" bo'lgach xodimga baholash imkoniyati ochilishi (1–5 yulduz + ixtiyoriy izoh)
- [ ] Baho faqat o'z murojaatiga va faqat bir marta berilishi
- [ ] Saytda: "Mening murojaatlarim" sahifasida baholash tugmasi
- [ ] **3 kun ichida baho qo'yilmasa** — bot orqali bir marta eslatma (10-bosqichda ulanadi)
- [ ] **7 kundan keyin** bahosiz avtomatik yopilishi (hisobotda "baholanmagan" bo'lib ko'rinadi)
- [ ] Usta profilida o'rtacha reyting ko'rinishi
- [ ] Past baho (1–2) qo'yilsa adminga bildirishnoma
- [ ] Baholar hisobotlarga ulanishi (11-bosqich)

**Natija:** ishlaydigan baholash tizimi va ustalar reytingi.

**Tugash mezoni:** topshirilgan har bir ta'mirni xodim baholay oladi; usta reytingi avtomatik hisoblanadi; baholanmaganlar 7 kunda avto-yopiladi.

---

## 10-bosqich. Telegram bot

**Maqsad:** murojaat yuborish, xabarnoma olish va baholashni Telegram orqali ham qilish.

**Vazifalar:**
- [ ] Bot yaratish (aiogram), token `.env` da
- [ ] Ro'yxatdan o'tish: xodim telefon raqami orqali tizimdagi profiliga bog'lanadi (`telegram_id` saqlanadi)
- [ ] Murojaat yuborish: qurilmani tanlash (yoki inventar raqam yozish) → muammo tavsifi → **shoshilinchlik** → **usta tanlash** (ixtiyoriy, "farqi yo'q" tugmasi bilan) → rasm (ixtiyoriy) → tasdiqlash
- [ ] "Mening murojaatlarim" — bot orqali holatlarni ko'rish
- [ ] Xodimga avtomatik xabarnomalar: "murojaat qabul qilindi", "ta'mirga olindi", "qurilmangiz tayyor — olib keting"
- [ ] **Ustalarga xabarnomalar:** navbatga yangi ta'mir tushganda (shoshilinch bo'lsa alohida belgi bilan); operator to'g'ridan-to'g'ri biriktirganda shaxsiy xabar; xodim uni shaxsan tanlaganda — "sizga so'ralgan yangi ta'mir" xabari (qabul/rad tugmalari bilan)
- [ ] Topshirilgandan keyin bot baholash so'rashi (1–5 tugmalar + izoh)
- [ ] **Baho eslatmasi:** 3 kundan keyin baholamaganlarga avtomatik eslatma (9-bosqich qoidasi)
- [ ] Operator/admin guruhiga yangi murojaat haqida bildirishnoma
- [ ] Django bilan umumiy baza orqali integratsiya (polling rejimida boshlash, deploy'da webhook)

**Natija:** to'liq ishlaydigan Telegram bot.

**Tugash mezoni:** xodim botdan murojaat yuborib, "tayyor" xabarini olib, botdan baho qo'ya oladi; ustalar yangi ishdan xabardor bo'ladi.

---

## 11-bosqich. Hisobotlar moduli

**Maqsad:** rahbariyat uchun oylik va yillik hisobotlar.

**Hisobot turlari:**
- [ ] **Oylik/yillik umumiy hisobot:** davr ichida nechta murojaat kelib tushdi, nechta ta'mir tugatildi, o'rtacha ta'mir muddati
- [ ] **Bosqichlar bo'yicha o'rtacha vaqt** (`StatusTarix` asosida): qabuldan tashxisgacha, tashxisdan ta'mirgacha, ta'mirdan topshirishgacha
- [ ] **Ustalar kesimida:** har bir usta nechta qurilma ta'mirlagan + **o'rtacha bahosi (reyting)** + **qayta ta'mirlar foizi** (sifat ko'rsatkichi) + **necha marta xodimlar tomonidan shaxsan so'ralgani** (ishonch ko'rsatkichi)
- [ ] **SLA buzilishlari:** davr ichida muddati o'tgan ta'mirlar soni va sabablari
- [ ] **Xodimlar kesimida:** kim necha marta murojaat qilgan / qurilma olib kelgan
- [ ] **O'zi ta'mirlanganlar:** qaysi xodim nechta qurilmani o'zi ta'mirlagan (faqat tasdiqlanganlari)
- [ ] **Bo'limlar kesimida:** qaysi bo'lim qurilmalari ko'p buziladi
- [ ] **Qurilmalar kesimida:** eng ko'p ta'mirlangan qurilmalar (almashtirish kerakligini ko'rsatadi)
- [ ] **Murojaat manbalari:** sayt / bot / operator orqali kelganlar nisbati
- [ ] **Xarajatlar:** davr bo'yicha ehtiyot qismlar va ta'mir xarajatlari

**Vazifalar:**
- [ ] Davr tanlash (oy/yil/ixtiyoriy oraliq) bilan hisobot sahifalari
- [ ] Diagrammalar (Chart.js): oylar bo'yicha murojaatlar, ustalar taqqoslash, reytinglar
- [ ] **Excel'ga eksport** (openpyxl)
- [ ] **PDF hisobot** (WeasyPrint) — chop etib rahbariyatga topshirish uchun
- [ ] Rahbariyat roli uchun alohida hisobot dashboard'i

**Natija:** oylik/yillik hisobotlar tizimi.

**Tugash mezoni:** "2026 yil iyun oyida kim nechta qurilma ta'mirlagan, reytingi va qayta ta'mir foizi qancha" savoliga 2 ta klik bilan Excel fayl olish mumkin.

---

## 12-bosqich. Testlash

**Maqsad:** real ishga tushirishdan oldin xatolardan tozalash.

**Vazifalar:**
- [ ] Modellar va asosiy view'lar uchun testlar yozish
- [ ] Murojaat → navbat → ta'mir → topshirish → baholash zanjirini to'liq qo'lda tekshirish
- [ ] **Navbat tekshiruvi:** ikki usta bir ta'mirni bir vaqtda olishga urinsa, faqat bittasiga tegishi; navbatda faqat eng eski 10 ta ko'rinishi
- [ ] **Usta tanlash tekshiruvi:** tanlangan usta rad etganda yoki 1 ish kuni javob bermaganda ta'mir umumiy navbatga qaytishi
- [ ] O'zi-ta'mir oqimini tekshirish: tasdiqlangani tarixga tushishi, rad etilgani tushmasligi
- [ ] **Excel import:** noto'g'ri fayl/qatorlarda tushunarli xato ko'rsatishi, to'g'ri fayl to'liq yuklanishi
- [ ] **SLA va qayta ta'mir:** muddati o'tganlar qizil ko'rinishi, 30 kun ichida qaytgan qurilma avtomatik belgilanishi
- [ ] **Avtoyopish:** 7 kunda baholanmagan ta'mir avto-yopilishi, eslatma bir marta ketishi
- [ ] Rollar tekshiruvi: xodim boshqa xodim murojaatini ko'rmasligi, usta hisobotga kirmasligi
- [ ] Baho faqat bir marta qo'yilishini tekshirish
- [ ] Bot ssenariylarini tekshirish (ro'yxatdan o'tish, murojaat, xabarnomalar, baho)
- [ ] Hisobot raqamlarini qo'lda hisoblab solishtirish
- [ ] Noto'g'ri ma'lumot kiritilganda forma xatolarni chiroyli ko'rsatishi
- [ ] Topilgan xatolarni tuzatish

**Natija:** barqaror versiya.

**Tugash mezoni:** kritik xatolar yo'q, hisobot raqamlari aniq, bot barqaror ishlaydi.

---

## 13-bosqich. Deploy va topshirish

**Maqsad:** tizimni universitet serveriga joylash.

**Vazifalar:**
- [ ] Server tayyorlash (universitet lokal serveri yoki VPS)
- [ ] Gunicorn + Nginx sozlash
- [ ] `DEBUG=False`, xavfsizlik sozlamalari, static fayllar
- [ ] Botni production rejimga o'tkazish (webhook yoki systemd service sifatida polling)
- [ ] SLA eslatmalari va avtoyopish uchun rejalashtirilgan vazifalar (cron / celery beat) sozlash
- [ ] Kunlik avtomatik backup (baza dump)
- [ ] Real ma'lumotlarni kiritish — Excel import orqali (qurilmalar, xodimlar), QR-kodlarni chop etib yopishtirish
- [ ] Foydalanuvchi qo'llanmasi yozish (xodim, operator va usta uchun alohida)
- [ ] Foydalanuvchilarni o'qitish

**Natija:** ishga tushirilgan tizim + bot + qo'llanma.

**Tugash mezoni:** xodimlar saytdan/botdan murojaat yuborib ishlay oladi; QR-kodlar qurilmalarga yopishtirilgan.

---

## 14-bosqich. Qo'llab-quvvatlash va rivojlantirish

**Doimiy vazifalar:**
- [ ] Backuplar ishlashini muntazam tekshirish
- [ ] Foydalanuvchi muammolarini tuzatish
- [ ] Kutubxonalarni yangilab borish

**Kelajakdagi g'oyalar:**
- [ ] REST API (Django REST Framework) — mobil ilova uchun
- [ ] Ehtiyot qismlar ombori moduli
- [ ] SMS xabarnomalar (Telegram ishlatmaydigan xodimlar uchun)

---

*Oxirgi yangilanish: 2026-07-23*
