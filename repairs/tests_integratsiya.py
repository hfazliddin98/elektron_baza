"""To'liq jarayon testi (12-bosqich).

Bitta murojaatning saytdan va botdan boshlanib, hisobotga tushishigacha
bo'lgan butun yo'lini bir joyda tekshiradi. Modullar orasidagi bog'lanish
buzilsa, shu test birinchi bo'lib ogohlantiradi.
"""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import AmalTarixi, User, Usta
from bot import baza as bot_baza
from devices.models import Bolim, Qurilma, Xodim
from reports.hisobot import Davr, yig

from .models import TamirYozuvi

Holat = TamirYozuvi.Holat


class ToliqJarayonTest(TestCase):
    """Sayt orqali: murojaat → qabul → navbat → ta'mir → topshirish → baho → hisobot."""

    @classmethod
    def setUpTestData(cls):
        cls.bolim = Bolim.objects.create(nomi='Kutubxona')
        cls.admin = User.objects.create_user(username='admin', rol=User.Rol.ADMIN)
        cls.operator = User.objects.create_user(username='op', rol=User.Rol.OPERATOR)
        cls.rahbar = User.objects.create_user(username='rah', rol=User.Rol.RAHBARIYAT)

        cls.usta_user = User.objects.create_user(username='usta', rol=User.Rol.USTA)
        cls.usta = Usta.objects.create(user=cls.usta_user, fio='Karimov Anvar')

        cls.xodim_user = User.objects.create_user(username='xodim', rol=User.Rol.XODIM)
        cls.xodim = Xodim.objects.create(
            user=cls.xodim_user, fio='Yusupova Malika', bolim=cls.bolim,
            telefon='+998901234567',
        )
        cls.qurilma = Qurilma.objects.create(
            inventar_raqami='UNI-0001', turi=Qurilma.Turi.PRINTER,
            bolim=cls.bolim, xodim=cls.xodim,
        )

    def test_saytdan_boshlab_hisobotgacha(self):
        # 1. Xodim murojaat yuboradi
        self.client.force_login(self.xodim_user)
        self.client.post(reverse('murojaat_yangi'), {
            'qurilma': self.qurilma.pk,
            'muhimlik': TamirYozuvi.Muhimlik.ODDIY,
            'muammo_tavsifi': "Printer qog'oz tortmayapti",
            'tanlangan_usta': self.usta.pk,
        })
        tamir = TamirYozuvi.objects.get()
        self.assertEqual(tamir.holat, Holat.YANGI)
        self.assertEqual(tamir.tanlangan_usta, self.usta)

        # 2. Operator qabul qiladi — ish navbatga tushadi
        self.client.force_login(self.operator)
        self.client.post(reverse('murojaat_qabul', args=[tamir.pk]))
        tamir.refresh_from_db()
        self.assertEqual(tamir.holat, Holat.QABUL)

        # 3. Ish so'ralgan ustaga tegishli — boshqa usta ololmaydi
        self.assertIn(tamir, TamirYozuvi.objects.ustaga_soralgan(self.usta))
        self.assertNotIn(tamir, TamirYozuvi.objects.erkin_navbat())

        # 4. Usta navbatdan o'ziga oladi
        self.client.force_login(self.usta_user)
        self.client.post(reverse('ishni_olish', args=[tamir.pk]))
        tamir.refresh_from_db()
        self.assertEqual(tamir.usta, self.usta)
        self.assertEqual(tamir.holat, Holat.TASHXIS)
        self.qurilma.refresh_from_db()
        self.assertEqual(self.qurilma.holati, Qurilma.Holat.TAMIRDA)

        # 5. Usta ishlaydi va yakunlaydi
        self.client.post(reverse('ishni_boshlash', args=[tamir.pk]))
        self.client.post(reverse('ishni_yakunlash', args=[tamir.pk]), {
            'yak-bajarilgan_ishlar': 'Kartrij almashtirildi',
            'yak-ehtiyot_qismlar': 'Kartrij — 1 dona',
            'yak-xarajat': '150000',
        })
        tamir.refresh_from_db()
        self.assertEqual(tamir.holat, Holat.TAYYOR)

        # 6. Operator topshiradi
        self.client.force_login(self.operator)
        self.client.post(reverse('topshirish', args=[tamir.pk]))
        tamir.refresh_from_db()
        self.assertEqual(tamir.holat, Holat.TOPSHIRILDI)
        self.qurilma.refresh_from_db()
        self.assertEqual(self.qurilma.holati, Qurilma.Holat.ISHLAMOQDA)

        # 7. Xodim baholaydi
        self.client.force_login(self.xodim_user)
        self.client.post(reverse('baho_berish', args=[tamir.pk]),
                         {'baho-baho': '5', 'baho-baho_izoh': 'Rahmat'})
        tamir.refresh_from_db()
        self.assertEqual(tamir.baho, 5)

        # 8. Butun yo'l tarixda saqlangan
        self.assertEqual(
            [s.yangi_holat for s in tamir.status_tarixi.all()],
            [Holat.YANGI, Holat.QABUL, Holat.TASHXIS, Holat.TAMIRDA,
             Holat.TAYYOR, Holat.TOPSHIRILDI],
        )

        # 9. Amallar tarixida asosiy qadamlar bor
        self.assertTrue(AmalTarixi.objects.filter(amal=AmalTarixi.Amal.YARATISH).exists())
        self.assertTrue(AmalTarixi.objects.filter(amal=AmalTarixi.Amal.HOLAT).exists())

        # 10. Hisobotga tushadi
        bugun = timezone.localdate()
        malumot = yig(Davr(bugun - timedelta(days=1), bugun + timedelta(days=1)))
        self.assertEqual(malumot['umumiy']['kelgan'], 1)
        self.assertEqual(malumot['umumiy']['tugatilgan'], 1)
        self.assertEqual(float(malumot['umumiy']['xarajat']), 150000)
        usta_qatori = next(u for u in malumot['ustalar'] if u.pk == self.usta.pk)
        self.assertEqual(usta_qatori.tamirlar_soni, 1)
        self.assertEqual(usta_qatori.reyting, 5)
        self.assertEqual(usta_qatori.soralgan_soni, 1)

        # 11. Rahbariyat hisobotni ko'ra oladi, Excel va PDF yuklab oladi
        self.client.force_login(self.rahbar)
        self.assertEqual(self.client.get(reverse('hisobot')).status_code, 200)
        self.assertTrue(self.client.get(reverse('hisobot_excel')).content)
        self.assertTrue(self.client.get(reverse('hisobot_pdf')).content.startswith(b'%PDF'))

    def test_botdan_boshlab_baholashgacha(self):
        # 1. Xodim telefon raqami orqali botga ulanadi
        tur, obyekt = bot_baza.foydalanuvchini_bogla(555000, '+998 90 123 45 67')
        self.assertEqual(tur, 'xodim')
        self.assertEqual(obyekt, self.xodim)

        # 2. Bot faqat o'z bo'limi qurilmalarini ko'rsatadi
        qurilmalar = bot_baza.xodim_qurilmalari(self.xodim)
        self.assertEqual([q.pk for q in qurilmalar], [self.qurilma.pk])

        # 3. Bot orqali murojaat yuboradi
        tamir = bot_baza.murojaat_yarat(
            self.xodim, self.qurilma.pk, 'Printer chirillayapti', shoshilinch=True,
        )
        self.assertEqual(tamir.manba, TamirYozuvi.Manba.BOT)
        self.assertEqual(tamir.muhimlik, TamirYozuvi.Muhimlik.SHOSHILINCH)

        # 4. Shoshilinch ish navbatning tepasida turadi
        tamir.holat_ozgartir(Holat.QABUL, user=self.operator)
        oddiy = TamirYozuvi.objects.create(
            qurilma=self.qurilma, xodim=self.xodim, muammo_tavsifi='Oddiy',
        )
        oddiy.holat_ozgartir(Holat.QABUL, user=self.operator)
        self.assertEqual(
            list(TamirYozuvi.objects.erkin_navbat().navbat_tartibi())[0], tamir,
        )

        # 5. Ta'mir yakunlanadi
        tamir.holat_ozgartir(Holat.TASHXIS, user=self.usta_user, usta=self.usta)
        tamir.holat_ozgartir(Holat.TAMIRDA, user=self.usta_user)
        tamir.holat_ozgartir(Holat.TAYYOR, user=self.usta_user)
        tamir.holat_ozgartir(Holat.TOPSHIRILDI, user=self.operator)

        # 6. Bot orqali baho qo'yiladi
        muvaffaqiyat, _ = bot_baza.baho_qoy(555000, tamir.pk, 4)
        self.assertTrue(muvaffaqiyat)
        tamir.refresh_from_db()
        self.assertEqual(tamir.baho, 4)

        # 7. Bot manbasi hisobotda ko'rinadi
        bugun = timezone.localdate()
        malumot = yig(Davr(bugun - timedelta(days=1), bugun + timedelta(days=1)))
        bot_manbasi = next(m for m in malumot['manbalar'] if m['nomi'] == 'Telegram bot')
        self.assertEqual(bot_manbasi['soni'], 1)

    def test_ozi_tamirlagan_tasdiqdan_keyin_hisobotga_tushadi(self):
        self.client.force_login(self.xodim_user)
        self.client.post(reverse('ozi_tamir_yangi'), {
            'qurilma': self.qurilma.pk,
            'muammo_tavsifi': 'Kabel uzilgan edi',
            'bajarilgan_ishlar': 'Kabelni almashtirdim',
            'ehtiyot_qismlar': 'HDMI kabel',
            'xarajat': '40000',
        })
        tamir = TamirYozuvi.objects.get(turi=TamirYozuvi.Turi.OZI)

        bugun = timezone.localdate()
        davr = Davr(bugun - timedelta(days=1), bugun + timedelta(days=1))
        self.assertEqual(yig(davr)['umumiy']['ozi_tamir'], 0)   # hali tasdiqlanmagan

        self.client.force_login(self.admin)
        self.client.post(reverse('tasdiq_qarori', args=[tamir.pk]),
                         {'tas-qaror': TamirYozuvi.Tasdiq.TASDIQLANDI, 'tas-izoh': ''})

        malumot = yig(davr)
        self.assertEqual(malumot['umumiy']['ozi_tamir'], 1)
        self.assertEqual(float(malumot['umumiy']['xarajat']), 40000)
        xodim_qatori = next(x for x in malumot['xodimlar'] if x.pk == self.xodim.pk)
        self.assertEqual(xodim_qatori.ozi_soni, 1)
