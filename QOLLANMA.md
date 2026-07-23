# Foydalanuvchi qo'llanmasi

**Elektron Baza** — universitet elektron qurilmalarini ro'yxatga olish va ta'mirlash tizimi.

Tizimga kirish: `https://baza.universitet.uz` · Login va parolni administrator beradi.
Birinchi kirgandan keyin **parolni o'zgartiring** (yuqori o'ng burchak → *Parolni o'zgartirish*).

---

## Kimga qaysi bo'lim ochiq

| Rol | Nima qila oladi |
|-----|-----------------|
| **Xodim** | Murojaat yuborish, holatini kuzatish, xizmatni baholash, o'zi ta'mirlaganini kiritish |
| **Usta** | Navbatdan ish olish, ta'mirni yuritish va yakunlash |
| **Operator** | Murojaatlarni qabul/rad qilish, qurilma topshirish, reestrni yuritish |
| **Admin** | Hammasi + o'zi-ta'mir hisobotlarini tasdiqlash, import, amallar tarixi |
| **Rahbariyat** | Hisobotlarni ko'rish (Excel/PDF) |

---

## 1. Xodim uchun

### Murojaat yuborish (sayt orqali)

1. Yuqoridagi menyudan **«Murojaat yuborish»** ni bosing.
2. Qurilmani tanlang (ro'yxatda o'z bo'limingiz qurilmalari chiqadi).
   - Qurilmadagi **QR-kodni** skanerlasangiz, o'sha qurilma sahifasi ochiladi —
     u yerda ham *«Ta'mirga murojaat yuborish»* tugmasi bor va qurilma tayyor tanlangan bo'ladi.
3. Muammoni **aniq yozing** — «ishlamayapti» emas, «yoqilganda qizil chiroq yonadi, ekran qorong'i».
4. **Shoshilinchlik**: «Shoshilinch» ni faqat dars yoki ish to'xtab qolgan hollarda tanlang.
5. **Usta** — xohlasangiz aniq bir ustani tanlaysiz. Tanlamasangiz («Farqi yo'q»)
   ish umumiy navbatga tushadi va bo'sh usta oladi — odatda bu tezroq.
6. Imkoni bo'lsa **rasm** biriktiring.

> Tanlangan usta 1 ish kunida javob bermasa, ish avtomatik umumiy navbatga o'tadi —
> murojaatingiz kutib qolmaydi.

### Murojaat yuborish (Telegram bot orqali)

1. Botni oching va **/start** yuboring.
2. **«Telefon raqamimni yuborish»** tugmasini bosing — tizim sizni tanib oladi.
   (Raqam tanilmasa, administratorga aytib, telefon raqamingizni tizimga kiritishni so'rang.)
3. **«🛠 Ta'mirga murojaat»** → qurilmani tanlang → muammoni yozing →
   shoshilinchlikni belgilang → ustani tanlang (yoki «Farqi yo'q»).

Bot sizga o'zi xabar beradi: murojaat qabul qilinganda, ta'mirga olinganda va
qurilma tayyor bo'lganda.

### Holatni kuzatish

**«Mening murojaatlarim»** bo'limida har bir murojaat holati ko'rinadi:

| Holat | Ma'nosi |
|-------|---------|
| Yangi murojaat | Operator hali ko'rib chiqmagan |
| Qabul qilindi (navbatda) | Qabul qilingan, usta olishini kutmoqda |
| Tashxisda | Usta muammoni aniqlamoqda |
| Ta'mirda | Ta'mir jarayonida |
| Tayyor | Ta'mir tugagan, topshirishni kutmoqda |
| Topshirildi | Qurilma sizga qaytarilgan |
| Rad etildi | Qabul qilinmadi — sababi ko'rsatilgan |

### Xizmatni baholash

Qurilma topshirilgach ta'mir sahifasida **«Xizmatni baholash»** tugmasi paydo bo'ladi
(1–5). Botda ham baho tugmalari keladi. Baho **bir marta** qo'yiladi.
3 kun ichida baholamasangiz bot bir marta eslatadi, 7 kundan keyin murojaat
bahosiz yopiladi.

### «O'zim ta'mirladim»

Qurilmani o'zingiz tuzatgan bo'lsangiz, **«O'zim ta'mirladim»** formasini to'ldiring:
nima buzilgan edi, nima qildingiz, qanday ehtiyot qism ishlatdingiz, xarajat.

Hisobot **admin tasdig'idan** keyin qurilma tarixiga va umumiy hisobotlarga qo'shiladi.
Rad etilsa, sababi bilan sizga ko'rinadi.

---

## 2. Usta uchun

### Ish olish

**«Navbat»** bo'limida ikki ro'yxat bor:

- **«Sizdan so'ralgan ishlar»** — xodim aynan sizni tanlagan.
  *Qabul qilish* yoki *Rad etish* (rad etsangiz ish umumiy navbatga qaytadi).
- **«Umumiy navbat»** — eng eski 10 ta ish, shoshilinchlari tepada.
  **«O'zimga olish»** tugmasi bilan ishni olasiz.

> Ishlar majburiy biriktirilmaydi — o'zingiz tanlaysiz. Faqat shoshilinch holatlarda
> operator to'g'ridan-to'g'ri biriktirishi mumkin.

Bir ishni faqat bitta usta oladi: kimdir sizdan oldin olgan bo'lsa, tizim ogohlantiradi.

### Ta'mirni yuritish

1. Ishni olganingizda holat **«Tashxisda»** bo'ladi.
2. Muammoni aniqlagach **«Ta'mirni boshlash»** → holat **«Ta'mirda»**.
3. Tugatgach **«Ishni yakunlash»**: bajarilgan ishlar (majburiy), ehtiyot qismlar, xarajat.
   → holat **«Tayyor»**, xodimga avtomatik xabar boradi.
4. Qurilmani xodimga operator topshiradi.

**«Mening ta'mirlarim»** bo'limida barcha ishlaringiz va o'rtacha bahoyingiz ko'rinadi.

> Har bir holat uchun muddat belgilangan. Muddat o'tsa ish ro'yxatda qizil belgi bilan
> ko'rinadi va adminga xabar boradi — ishni cho'zib yubormaslikka harakat qiling.

---

## 3. Operator uchun

### Murojaatlarni ko'rib chiqish

**«Murojaatlar»** bo'limida yangi murojaatlar turadi (shoshilinchlar tepada).
Har birini oching va:

- **«Qabul qilish»** — ish navbatga tushadi, ustalarga xabar boradi.
- **«Rad etish»** — sababini yozing (xodimga shu sabab ko'rinadi va botga yuboriladi).

Xodim qurilmani **o'zi olib kelgan** bo'lsa: **«Qabul qilish»** tugmasi (yoki
*Ta'mirlar → Qabul qilish*) orqali murojaatni o'zingiz ochasiz — u darhol navbatga tushadi.

### Ustaga biriktirish (faqat shoshilinch holatlarda)

Odatda usta ishni o'zi oladi. Shoshilinch ishni kutib turmaslik uchun
ta'mir sahifasida **«Ustaga biriktirish»** tugmasidan foydalaning.

### Qurilmani topshirish

Holat **«Tayyor»** bo'lganda **«Xodimga topshirish»** tugmasini bosing.
Shundan keyin qurilma holati «Ishlamoqda» ga qaytadi va xodim baho bera oladi.

### Qurilmalar reestri

**«Qurilmalar»** bo'limida qidiruv va filtr bor. Yangi qurilma qo'shish,
tahrirlash, yaroqsizga chiqarish (yozuv o'chirilmaydi — tarix saqlanadi) mumkin.

---

## 4. Admin uchun

### Kundalik ishlar

- **«Tasdiqlash»** — xodimlarning «o'zim ta'mirladim» hisobotlari.
  Har birini ko'rib chiqing: tasdiqlash yoki rad etish (rad etilsa sabab majburiy).
- **Panel**dagi **«Muddati o'tgan (SLA)»** raqamiga qarab turing —
  bosilsa kechikkan ta'mirlar ro'yxati ochiladi.
- **«Amal tarixi»** — kim qachon nima qilgani (kirish, tasdiqlash, status o'zgarishlari).

### Ma'lumotlarni kiritish

**Ma'lumotnoma** menyusi:

- **Bo'limlar**, **Xodimlar** — qo'lda qo'shish/tahrirlash.
- **Qurilmalarni / Xodimlarni import qilish** — Excel orqali ommaviy yuklash.
  Avval **shablonni yuklab oling**, to'ldiring, keyin yuklang.
  Xato qatorlar raqami bilan ko'rsatiladi; tuzatilgan faylni qayta yuklash xavfsiz —
  mavjud yozuvlar takrorlanmaydi.
- **QR yorliqlarni chop etish** — filtrlab (masalan, bitta bo'limni) chop etasiz.

### Foydalanuvchilar va rollar

Admin panel (`/admin/`) → *Foydalanuvchilar*:

1. Foydalanuvchi yarating, **rolini** belgilang.
2. Xodim yoki usta yozuvini o'sha foydalanuvchiga **biriktiring**
   (*Xodimlar* / *Ustalar* bo'limida «Foydalanuvchi (login)» maydoni).

> Biriktirilmasa, foydalanuvchi tizimga kiradi-yu, lekin murojaat yubora olmaydi —
> panelda ogohlantirish ko'rsatiladi.

---

## 5. Rahbariyat uchun

**«Hisobotlar»** bo'limi. Yuqorida davrni tanlaysiz (yoki tayyor tugmalar:
*Shu oy*, *O'tgan oy*, *Shu yil*, *O'tgan yil*).

Hisobotda:

- Umumiy ko'rsatkichlar: kelib tushgan, tugatilgan, jarayonda, muddati o'tgan,
  o'rtacha ta'mir muddati, o'rtacha baho, jami xarajat.
- **Ustalar kesimida**: kim nechta qurilma ta'mirlagan, reytingi, qayta ta'mir foizi
  (sifat ko'rsatkichi), necha marta shaxsan so'ralgani (ishonch ko'rsatkichi).
- **Xodimlar kesimida**: kim necha marta murojaat qilgan, kim o'zi ta'mirlagan.
- **Bo'limlar** va **eng ko'p ta'mirlangan qurilmalar** (almashtirish kerakligini ko'rsatadi).
- Bosqichlar bo'yicha o'rtacha vaqt: qayerda vaqt yo'qolayotgani ko'rinadi.
- Diagrammalar: oylar bo'yicha dinamika, ustalar taqqoslash, murojaat manbalari.

O'ng yuqorida **Excel** va **PDF** tugmalari — tanlangan davr uchun to'liq hisobotni
yuklab oladi (PDF chop etishga tayyor).

---

## Tez-tez so'raladigan savollar

**Parolni unutdim.** Administratorga murojaat qiling — u admin paneldan yangi parol qo'yadi.

**Bot meni tanimayapti.** Telefon raqamingiz tizimda yozilgan bo'lishi kerak.
Administrator *Xodimlar* bo'limida raqamingizni kiritsin, keyin botga qaytadan
**/start** yuboring.

**Murojaatimni bekor qilsam bo'ladimi?** Operatorga ayting — u murojaatni sabab bilan
rad etadi. Tarixda yozuv qoladi.

**Qurilmam ro'yxatda yo'q.** U hali reestrga kiritilmagan yoki boshqa bo'limga biriktirilgan.
Operator yoki adminga murojaat qiling.

**Nega ta'mirim uzoq davom etmoqda?** Ta'mir sahifasidagi *Holatlar tarixi* har bir
bosqich qachon boshlangani ko'rsatadi. Muddat oshgan bo'lsa qizil belgi turadi va
admin bundan xabardor bo'ladi.
