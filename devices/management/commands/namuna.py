"""Ishlab chiqish uchun namunaviy ma'lumotlar: `python manage.py namuna`.

Qayta ishga tushirilsa mavjud yozuvlarni takrorlamaydi.
DIQQAT: faqat ishlab chiqish muhiti uchun — parollar oddiy.
"""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User, Usta
from devices.models import Bolim, Qurilma, Xodim
from repairs.models import TamirYozuvi

MUAMMOLAR = [
    "Kompyuter yoqilmayapti, ko'k ekran chiqmoqda",
    "Printer qog'oz tortmayapti",
    "Monitor signal ko'rsatmayapti",
    "Sichqoncha va klaviatura ishlamayapti",
    "Proyektor lampasi xira yonmoqda",
    "Tizim juda sekin ishlayapti",
    "MFU skanerlash rejimida xato bermoqda",
    "Ovoz chiqmayapti",
    "Internet kabeli ulanmayapti",
    "Kartrij siyoh oqizmoqda",
]

ISHLAR = [
    'Ehtiyot qism almashtirildi, tizim tozalandi.',
    'Drayverlar qayta o\'rnatildi.',
    'Kartrij almashtirildi, pechat boshi tozalandi.',
    'Blok pitaniya almashtirildi.',
    'Chang tozalandi, termopasta yangilandi.',
    'Kabel almashtirildi.',
]

QISMLAR = ['Kartrij — 1 dona', 'HDMI kabel — 1 dona', 'Blok pitaniya — 1 dona',
           'Termopasta', 'Sichqoncha — 1 dona', '']


class Command(BaseCommand):
    help = "Namunaviy ma'lumotlar yaratadi (bo'limlar, xodimlar, ustalar, qurilmalar, ta'mirlar)"

    @transaction.atomic
    def handle(self, *args, **options):
        tasodif = random.Random(2026)  # har safar bir xil ma'lumot chiqishi uchun

        # --- Foydalanuvchilar ---
        admin, yaratildi = User.objects.get_or_create(
            username='admin',
            defaults={'rol': User.Rol.ADMIN, 'is_staff': True, 'is_superuser': True,
                      'first_name': 'Admin'},
        )
        if yaratildi:
            admin.set_password('admin123')
            admin.save()

        operator, yaratildi = User.objects.get_or_create(
            username='operator',
            defaults={'rol': User.Rol.OPERATOR, 'first_name': 'Dilshod', 'last_name': 'Ergashev'},
        )
        if yaratildi:
            operator.set_password('operator123')
            operator.save()

        rahbar, yaratildi = User.objects.get_or_create(
            username='rahbar',
            defaults={'rol': User.Rol.RAHBARIYAT, 'first_name': 'Shuhrat',
                      'last_name': 'Abdullayev'},
        )
        if yaratildi:
            rahbar.set_password('rahbar123')
            rahbar.save()

        # --- Bo'limlar ---
        at_markazi = Bolim.objects.get_or_create(
            nomi='Axborot texnologiyalari markazi', defaults={'bino': 'A bino', 'xona': '101'})[0]
        fizmat = Bolim.objects.get_or_create(
            nomi='Fizika-matematika fakulteti', defaults={'bino': 'B bino', 'xona': '210'})[0]
        kutubxona = Bolim.objects.get_or_create(
            nomi='Kutubxona', defaults={'bino': 'Asosiy bino', 'xona': '1-qavat'})[0]

        # --- Ustalar ---
        ustalar = {}
        usta_royxati = [
            ('usta1', 'Karimov Anvar', 'Kompyuter va noutbuklar', '+998901112233'),
            ('usta2', 'Tosheva Nilufar', 'Printer va MFU', '+998901112244'),
            ('usta3', 'Rahimov Bekzod', 'Elektronika', '+998901112255'),
            ('usta4', 'Aliyev Sardor', 'Umumiy texnika', '+998901112266'),
        ]
        for username, fio, mutaxassislik, telefon in usta_royxati:
            user, yaratildi = User.objects.get_or_create(
                username=username,
                defaults={'rol': User.Rol.USTA,
                          'first_name': fio.split()[1], 'last_name': fio.split()[0]},
            )
            if yaratildi:
                user.set_password('usta123')
                user.save()
            ustalar[fio] = Usta.objects.get_or_create(
                fio=fio,
                defaults={'user': user, 'mutaxassisligi': mutaxassislik, 'telefon': telefon},
            )[0]

        # --- Xodimlar ---
        xodimlar = {}
        xodim_royxati = [
            ('xodim1', 'Yusupova Malika', fizmat, 'Dekan kotibasi', '+998902223311'),
            ('xodim2', 'Qodirov Jasur', at_markazi, 'Muhandis', '+998902223322'),
            ('xodim3', 'Ismoilova Dilnoza', kutubxona, 'Kutubxonachi', '+998902223333'),
            ('xodim4', "Nazarov Ulug'bek", fizmat, "O'qituvchi", '+998902223344'),
            ('xodim5', 'Saidova Gulnora', at_markazi, 'Laborant', '+998902223355'),
            ('xodim6', 'Hamidov Otabek', kutubxona, 'Mutaxassis', '+998902223366'),
        ]
        for username, fio, bolim, lavozim, telefon in xodim_royxati:
            user, yaratildi = User.objects.get_or_create(
                username=username,
                defaults={'rol': User.Rol.XODIM,
                          'first_name': fio.split()[1], 'last_name': fio.split()[0]},
            )
            if yaratildi:
                user.set_password('xodim123')
                user.save()
            xodimlar[fio] = Xodim.objects.get_or_create(
                fio=fio,
                defaults={'user': user, 'bolim': bolim, 'lavozimi': lavozim, 'telefon': telefon},
            )[0]

        # --- Qurilmalar ---
        qurilmalar = {}
        qurilma_royxati = [
            ('UNI-0001', Qurilma.Turi.KOMPYUTER, 'HP ProDesk 400 G7', at_markazi, 'Qodirov Jasur'),
            ('UNI-0002', Qurilma.Turi.KOMPYUTER, 'Lenovo ThinkCentre M75', fizmat, "Nazarov Ulug'bek"),
            ('UNI-0003', Qurilma.Turi.MONITOR, 'Samsung F24T350', at_markazi, 'Qodirov Jasur'),
            ('UNI-0004', Qurilma.Turi.PRINTER, 'HP LaserJet P1102', fizmat, 'Yusupova Malika'),
            ('UNI-0005', Qurilma.Turi.MFU, 'Canon i-SENSYS MF3010', kutubxona, 'Ismoilova Dilnoza'),
            ('UNI-0006', Qurilma.Turi.PROYEKTOR, 'Epson EB-X06', fizmat, None),
            ('UNI-0007', Qurilma.Turi.KOMPYUTER, 'Acer Veriton X2665G', kutubxona, 'Hamidov Otabek'),
            ('UNI-0008', Qurilma.Turi.UPS, 'APC Back-UPS 650', at_markazi, None),
            ('UNI-0009', Qurilma.Turi.SKANER, 'Canon CanoScan LiDE 300', kutubxona, None),
            ('UNI-0010', Qurilma.Turi.PRINTER, 'Epson L3210', at_markazi, 'Saidova Gulnora'),
            ('UNI-0011', Qurilma.Turi.MONITOR, 'LG 22MK430', fizmat, "Nazarov Ulug'bek"),
            ('UNI-0012', Qurilma.Turi.KOMPYUTER, 'HP EliteDesk 800 G5', at_markazi, 'Saidova Gulnora'),
        ]
        for inventar, turi, model_nomi, bolim, xodim_fio in qurilma_royxati:
            qurilmalar[inventar] = Qurilma.objects.get_or_create(
                inventar_raqami=inventar,
                defaults={'turi': turi, 'modeli': model_nomi, 'bolim': bolim,
                          'xodim': xodimlar.get(xodim_fio)},
            )[0]

        # --- Ta'mir yozuvlari (faqat birinchi ishga tushirishda) ---
        if not TamirYozuvi.objects.exists():
            self._tamirlar_yarat(tasodif, qurilmalar, xodimlar, ustalar, operator, admin)

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {Bolim.objects.count()} bo'lim, {Xodim.objects.count()} xodim, "
            f"{Usta.objects.count()} usta, {Qurilma.objects.count()} qurilma, "
            f"{TamirYozuvi.objects.count()} ta'mir yozuvi."
        ))
        self.stdout.write("Kirish (faqat dev): admin/admin123, operator/operator123, "
                          "rahbar/rahbar123, usta1..4/usta123, xodim1..6/xodim123")

    def _tamirlar_yarat(self, tasodif, qurilmalar, xodimlar, ustalar, operator, admin):
        """Oxirgi 12 oy uchun turli holatdagi ta'mirlar (hisobotlarni ko'rish uchun)."""
        endi = timezone.now()
        qurilma_royxati = list(qurilmalar.values())
        xodim_royxati = list(xodimlar.values())
        usta_royxati = list(ustalar.values())

        # 1. Tugallangan va baholangan ta'mirlar — oxirgi 12 oyga taqsimlangan
        for i in range(30):
            kun_oldin = tasodif.randint(10, 360)
            qurilma = tasodif.choice(qurilma_royxati)
            xodim = qurilma.xodim or tasodif.choice(xodim_royxati)
            usta = tasodif.choice(usta_royxati)

            tamir = TamirYozuvi.objects.create(
                qurilma=qurilma, xodim=xodim,
                manba=tasodif.choice([TamirYozuvi.Manba.SAYT, TamirYozuvi.Manba.BOT,
                                      TamirYozuvi.Manba.OPERATOR]),
                muhimlik=(TamirYozuvi.Muhimlik.SHOSHILINCH if tasodif.random() < 0.2
                          else TamirYozuvi.Muhimlik.ODDIY),
                muammo_tavsifi=tasodif.choice(MUAMMOLAR),
            )
            tamir.holat_ozgartir(TamirYozuvi.Holat.QABUL, user=operator)
            tamir.holat_ozgartir(TamirYozuvi.Holat.TASHXIS, user=usta.user, usta=usta)
            tamir.holat_ozgartir(TamirYozuvi.Holat.TAMIRDA, user=usta.user)
            tamir.bajarilgan_ishlar = tasodif.choice(ISHLAR)
            tamir.ehtiyot_qismlar = tasodif.choice(QISMLAR)
            tamir.xarajat = tasodif.choice([0, 40000, 85000, 150000, 220000, 310000])
            tamir.holat_ozgartir(TamirYozuvi.Holat.TAYYOR, user=usta.user)
            tamir.holat_ozgartir(TamirYozuvi.Holat.TOPSHIRILDI, user=operator)

            boshlanish = endi - timedelta(days=kun_oldin)
            tugash = boshlanish + timedelta(days=tasodif.randint(1, 6))
            TamirYozuvi.objects.filter(pk=tamir.pk).update(
                qabul_sana=boshlanish,
                navbatga_tushgan=boshlanish,
                boshlangan_sana=boshlanish + timedelta(hours=6),
                tugagan_sana=tugash,
                topshirilgan_sana=tugash,
                holat_sana=tugash,
                baho=tasodif.choices([5, 4, 3, 2], weights=[55, 30, 10, 5])[0],
                baho_sana=tugash,
                baho_izoh=tasodif.choice(['Rahmat, tez ishladingiz!', '', 'Yaxshi', '']),
            )

        # 2. Jarayondagi ta'mirlar
        yangi = TamirYozuvi.objects.create(
            qurilma=qurilmalar['UNI-0004'], xodim=xodimlar['Yusupova Malika'],
            manba=TamirYozuvi.Manba.SAYT,
            muammo_tavsifi="Printer qog'oz tortmayapti, chirillagan ovoz chiqaryapti.",
        )

        navbatda = TamirYozuvi.objects.create(
            qurilma=qurilmalar['UNI-0007'], xodim=xodimlar['Hamidov Otabek'],
            manba=TamirYozuvi.Manba.BOT, tanlangan_usta=ustalar['Karimov Anvar'],
            muammo_tavsifi="Kompyuter juda sekin ishlayapti, ba'zida o'zi o'chib qoladi.",
        )
        navbatda.holat_ozgartir(TamirYozuvi.Holat.QABUL, user=operator)

        erkin = TamirYozuvi.objects.create(
            qurilma=qurilmalar['UNI-0009'], xodim=xodimlar['Ismoilova Dilnoza'],
            manba=TamirYozuvi.Manba.SAYT,
            muammo_tavsifi='Skaner kompyuterga ulanmayapti.',
        )
        erkin.holat_ozgartir(TamirYozuvi.Holat.QABUL, user=operator)

        tamirda = TamirYozuvi.objects.create(
            qurilma=qurilmalar['UNI-0006'], xodim=xodimlar["Nazarov Ulug'bek"],
            muhimlik=TamirYozuvi.Muhimlik.SHOSHILINCH,
            muammo_tavsifi="Proyektor dars vaqtida o'chib qoldi, umuman yonmayapti.",
        )
        tamirda.holat_ozgartir(TamirYozuvi.Holat.QABUL, user=operator)
        tamirda.holat_ozgartir(TamirYozuvi.Holat.TASHXIS, user=ustalar['Rahimov Bekzod'].user,
                               usta=ustalar['Rahimov Bekzod'])
        tamirda.holat_ozgartir(TamirYozuvi.Holat.TAMIRDA, user=ustalar['Rahimov Bekzod'].user)

        # 3. O'zi ta'mirlagan — biri tasdiq kutmoqda, biri tasdiqlangan
        TamirYozuvi.objects.create(
            qurilma=qurilmalar['UNI-0003'], xodim=xodimlar['Qodirov Jasur'],
            turi=TamirYozuvi.Turi.OZI, manba=TamirYozuvi.Manba.SAYT,
            muammo_tavsifi="Monitor signal yo'qotib qolgan edi.",
            bajarilgan_ishlar='HDMI kabel yaroqsiz chiqdi, yangisiga almashtirdim.',
            ehtiyot_qismlar='HDMI kabel 1.5m — 1 dona', xarajat=40000,
        )

        tasdiqlangan = TamirYozuvi.objects.create(
            qurilma=qurilmalar['UNI-0011'], xodim=xodimlar["Nazarov Ulug'bek"],
            turi=TamirYozuvi.Turi.OZI, manba=TamirYozuvi.Manba.SAYT,
            muammo_tavsifi='Monitor kabeli bo\'shab qolgan edi.',
            bajarilgan_ishlar='Kabelni qayta uladim, mahkamladim.', xarajat=0,
        )
        tasdiqlangan.tasdiq_holati = TamirYozuvi.Tasdiq.TASDIQLANDI
        tasdiqlangan.tasdiqlagan = admin
        tasdiqlangan.tasdiq_sana = timezone.now()
        tasdiqlangan._ozgartirgan_user = admin
        tasdiqlangan.save()
