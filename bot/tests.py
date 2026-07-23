from unittest.mock import patch

from django.test import TestCase, override_settings

from accounts.models import User, Usta
from devices.models import Bolim, Qurilma, Xodim
from repairs.models import TamirYozuvi

from . import baza, xabar

Holat = TamirYozuvi.Holat


class TelefonTest(TestCase):
    def test_turli_formatlar_bir_xil_tozalanadi(self):
        for raqam in ['+998901234567', '998901234567', '90 123 45 67',
                      '+998 (90) 123-45-67', '901234567']:
            with self.subTest(raqam=raqam):
                self.assertEqual(baza.telefon_tozala(raqam), '901234567')

    def test_qisqa_raqam(self):
        self.assertEqual(baza.telefon_tozala('123'), '123')
        self.assertEqual(baza.telefon_tozala(''), '')
        self.assertEqual(baza.telefon_tozala(None), '')


class BoglashTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.bolim = Bolim.objects.create(nomi='Kutubxona')
        cls.xodim = Xodim.objects.create(
            fio='Xodim Bir', bolim=cls.bolim, telefon='+998901234567',
        )
        cls.usta = Usta.objects.create(fio='Usta Bir', telefon='998911112233')

    def test_xodim_telefon_orqali_boglanadi(self):
        tur, obyekt = baza.foydalanuvchini_bogla(111, '901234567')
        self.assertEqual(tur, 'xodim')
        self.assertEqual(obyekt, self.xodim)
        self.xodim.refresh_from_db()
        self.assertEqual(self.xodim.telegram_id, 111)

    def test_usta_telefon_orqali_boglanadi(self):
        tur, obyekt = baza.foydalanuvchini_bogla(222, '+998 91 111 22 33')
        self.assertEqual(tur, 'usta')
        self.assertEqual(obyekt, self.usta)

    def test_notanish_raqam(self):
        tur, obyekt = baza.foydalanuvchini_bogla(333, '+998900000000')
        self.assertIsNone(tur)
        self.assertIsNone(obyekt)

    def test_bitta_telegram_id_faqat_bitta_profilga_biriktiriladi(self):
        baza.foydalanuvchini_bogla(444, '901234567')       # xodim
        baza.foydalanuvchini_bogla(444, '911112233')       # endi usta

        self.xodim.refresh_from_db()
        self.usta.refresh_from_db()
        self.assertIsNone(self.xodim.telegram_id)
        self.assertEqual(self.usta.telegram_id, 444)


class BotMurojaatTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.bolim = Bolim.objects.create(nomi='Kutubxona')
        cls.boshqa = Bolim.objects.create(nomi='Dekanat')
        cls.xodim = Xodim.objects.create(
            fio='Xodim Bir', bolim=cls.bolim, telefon='+998901234567', telegram_id=555,
        )
        cls.usta_user = User.objects.create_user(username='u', rol=User.Rol.USTA)
        cls.usta = Usta.objects.create(user=cls.usta_user, fio='Usta Bir')
        cls.operator = User.objects.create_user(username='o', rol=User.Rol.OPERATOR)

        cls.qurilma = Qurilma.objects.create(
            inventar_raqami='UNI-0001', turi=Qurilma.Turi.PRINTER, bolim=cls.bolim,
        )
        Qurilma.objects.create(
            inventar_raqami='UNI-0002', turi=Qurilma.Turi.MONITOR, bolim=cls.boshqa,
        )

    def test_xodim_faqat_oz_bolimi_qurilmalarini_koradi(self):
        qurilmalar = baza.xodim_qurilmalari(self.xodim)
        self.assertEqual([q.inventar_raqami for q in qurilmalar], ['UNI-0001'])

    def test_bot_orqali_murojaat_yaratiladi(self):
        tamir = baza.murojaat_yarat(
            self.xodim, self.qurilma.pk, 'Printer ishlamayapti',
            shoshilinch=True, usta_id=self.usta.pk,
        )
        self.assertEqual(tamir.manba, TamirYozuvi.Manba.BOT)
        self.assertEqual(tamir.muhimlik, TamirYozuvi.Muhimlik.SHOSHILINCH)
        self.assertEqual(tamir.tanlangan_usta, self.usta)
        self.assertEqual(tamir.holat, Holat.YANGI)

    def test_bot_orqali_baholash(self):
        tamir = baza.murojaat_yarat(self.xodim, self.qurilma.pk, 'Test')
        tamir.holat_ozgartir(Holat.QABUL, user=self.operator)
        tamir.holat_ozgartir(Holat.TASHXIS, user=self.usta_user, usta=self.usta)
        tamir.holat_ozgartir(Holat.TAYYOR, user=self.usta_user)
        tamir.holat_ozgartir(Holat.TOPSHIRILDI, user=self.operator)

        muvaffaqiyat, _ = baza.baho_qoy(555, tamir.pk, 5)
        self.assertTrue(muvaffaqiyat)
        tamir.refresh_from_db()
        self.assertEqual(tamir.baho, 5)

        # Ikkinchi marta baholab bo'lmaydi
        muvaffaqiyat, xabar_matni = baza.baho_qoy(555, tamir.pk, 1)
        self.assertFalse(muvaffaqiyat)
        tamir.refresh_from_db()
        self.assertEqual(tamir.baho, 5)

    def test_begona_tamirni_baholab_bolmaydi(self):
        boshqa_xodim = Xodim.objects.create(fio='Boshqa', bolim=self.bolim, telegram_id=666)
        tamir = baza.murojaat_yarat(boshqa_xodim, self.qurilma.pk, 'Test')
        muvaffaqiyat, _ = baza.baho_qoy(555, tamir.pk, 5)
        self.assertFalse(muvaffaqiyat)

    def test_ulanmagan_foydalanuvchi_baholay_olmaydi(self):
        muvaffaqiyat, xabar_matni = baza.baho_qoy(999999, 1, 5)
        self.assertFalse(muvaffaqiyat)
        self.assertIn('/start', xabar_matni)


class XabarYuborishTest(TestCase):
    @override_settings(BOT_TOKEN='')
    def test_token_yoq_bolsa_xato_bermaydi(self):
        self.assertFalse(xabar.xabar_yubor(123, 'salom'))
        self.assertFalse(xabar.adminlarga('salom'))

    @override_settings(BOT_TOKEN='test-token')
    def test_telegram_ishlamasa_dastur_yiqilmaydi(self):
        with patch('bot.xabar.urllib.request.urlopen', side_effect=OSError('tarmoq yo\'q')):
            self.assertFalse(xabar.xabar_yubor(123, 'salom'))

    @override_settings(BOT_TOKEN='test-token')
    def test_telegram_id_yoq_bolsa_yuborilmaydi(self):
        with patch('bot.xabar.urllib.request.urlopen') as soxta:
            self.assertFalse(xabar.xabar_yubor(None, 'salom'))
            soxta.assert_not_called()


class BotBuyruqTest(TestCase):
    @override_settings(BOT_TOKEN='')
    def test_tokensiz_bot_buyrugi_tushunarli_xato_beradi(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError

        with self.assertRaises(CommandError) as kontekst:
            call_command('bot')
        self.assertIn('BOT_TOKEN', str(kontekst.exception))

    def test_handlerlar_yuklanadi(self):
        """aiogram router va dispatcher xatosiz quriladi."""
        from aiogram import Dispatcher

        from bot.handlers import router

        dp = Dispatcher()
        dp.include_router(router)
        self.assertTrue(router.observers['message'].handlers)
        self.assertTrue(router.observers['callback_query'].handlers)
