"""Ishlab chiqish uchun namunaviy ma'lumotlar: `python manage.py namuna`.

Qayta ishga tushirilsa mavjud yozuvlarni takrorlamaydi.
DIQQAT: faqat ishlab chiqish muhiti uchun — parollar oddiy.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User, Usta
from devices.models import Bolim, Qurilma, Xodim
from repairs.models import TamirYozuvi


class Command(BaseCommand):
    help = "Namunaviy ma'lumotlar yaratadi (bo'limlar, xodimlar, ustalar, qurilmalar, ta'mirlar)"

    @transaction.atomic
    def handle(self, *args, **options):
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
            defaults={'rol': User.Rol.RAHBARIYAT, 'first_name': 'Shuhrat', 'last_name': 'Abdullayev'},
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
            # 1. Yangi murojaat (saytdan)
            TamirYozuvi.objects.create(
                qurilma=qurilmalar['UNI-0004'], xodim=xodimlar['Yusupova Malika'],
                manba=TamirYozuvi.Manba.SAYT,
                muammo_tavsifi="Printer qog'oz tortmayapti, chirillagan ovoz chiqaryapti.",
            )

            # 2. Navbatda (botdan, xodim ustani o'zi tanlagan)
            t2 = TamirYozuvi.objects.create(
                qurilma=qurilmalar['UNI-0007'], xodim=xodimlar['Hamidov Otabek'],
                manba=TamirYozuvi.Manba.BOT,
                tanlangan_usta=ustalar['Karimov Anvar'],
                muammo_tavsifi="Kompyuter juda sekin ishlayapti, ba'zida o'zi o'chib qoladi.",
            )
            t2.holat_ozgartir(TamirYozuvi.Holat.QABUL, user=operator)

            # 3. Ta'mirda (shoshilinch, usta olgan)
            t3 = TamirYozuvi.objects.create(
                qurilma=qurilmalar['UNI-0006'], xodim=xodimlar["Nazarov Ulug'bek"],
                muhimlik=TamirYozuvi.Muhimlik.SHOSHILINCH,
                muammo_tavsifi="Proyektor dars vaqtida o'chib qoldi, umuman yonmayapti.",
            )
            t3.holat_ozgartir(TamirYozuvi.Holat.QABUL, user=operator)
            t3.usta = ustalar['Rahimov Bekzod']
            t3.holat_ozgartir(TamirYozuvi.Holat.TASHXIS, user=ustalar['Rahimov Bekzod'].user)
            t3.holat_ozgartir(TamirYozuvi.Holat.TAMIRDA, user=ustalar['Rahimov Bekzod'].user)

            # 4. Topshirilgan va baholangan
            t4 = TamirYozuvi.objects.create(
                qurilma=qurilmalar['UNI-0010'], xodim=xodimlar['Saidova Gulnora'],
                muammo_tavsifi='Printer kartriji siyoh oqizyapti, chop etganda dog\' qoladi.',
            )
            t4.holat_ozgartir(TamirYozuvi.Holat.QABUL, user=operator)
            t4.usta = ustalar['Tosheva Nilufar']
            t4.holat_ozgartir(TamirYozuvi.Holat.TASHXIS, user=ustalar['Tosheva Nilufar'].user)
            t4.holat_ozgartir(TamirYozuvi.Holat.TAMIRDA, user=ustalar['Tosheva Nilufar'].user)
            t4.bajarilgan_ishlar = 'Kartrij almashtirildi, pechat boshi tozalandi.'
            t4.ehtiyot_qismlar = 'Epson 003 kartrij — 1 dona'
            t4.xarajat = 150000
            t4.holat_ozgartir(TamirYozuvi.Holat.TAYYOR, user=ustalar['Tosheva Nilufar'].user)
            t4.holat_ozgartir(TamirYozuvi.Holat.TOPSHIRILDI, user=operator)
            t4.baho = 5
            t4.baho_izoh = 'Tez va sifatli ta\'mirlandi, rahmat!'
            t4.save()

            # 5. O'zi ta'mirlagan (tasdiq kutilmoqda)
            TamirYozuvi.objects.create(
                qurilma=qurilmalar['UNI-0003'], xodim=xodimlar['Qodirov Jasur'],
                turi=TamirYozuvi.Turi.OZI, manba=TamirYozuvi.Manba.SAYT,
                muammo_tavsifi='Monitor signal yo\'qotib qolgan edi.',
                bajarilgan_ishlar='HDMI kabel yaroqsiz chiqdi, yangisiga almashtirdim.',
                ehtiyot_qismlar='HDMI kabel 1.5m — 1 dona',
                xarajat=40000,
            )

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {Bolim.objects.count()} bo'lim, {Xodim.objects.count()} xodim, "
            f"{Usta.objects.count()} usta, {Qurilma.objects.count()} qurilma, "
            f"{TamirYozuvi.objects.count()} ta'mir yozuvi."
        ))
        self.stdout.write("Kirish (faqat dev): admin/admin123, operator/operator123, "
                          "rahbar/rahbar123, usta1..4/usta123, xodim1..6/xodim123")
