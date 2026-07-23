from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, Usta
from devices.models import Bolim, Qurilma, Xodim

from .models import TamirYozuvi

Holat = TamirYozuvi.Holat
Tasdiq = TamirYozuvi.Tasdiq


class AsosTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.bolim = Bolim.objects.create(nomi='Kutubxona')
        cls.boshqa_bolim = Bolim.objects.create(nomi='Dekanat')

        cls.admin = User.objects.create_user(username='a', rol=User.Rol.ADMIN)
        cls.operator = User.objects.create_user(username='o', rol=User.Rol.OPERATOR)
        cls.rahbar = User.objects.create_user(username='r', rol=User.Rol.RAHBARIYAT)

        cls.usta_user = User.objects.create_user(username='u1', rol=User.Rol.USTA)
        cls.usta2_user = User.objects.create_user(username='u2', rol=User.Rol.USTA)
        cls.usta = Usta.objects.create(user=cls.usta_user, fio='Usta Bir')
        cls.usta2 = Usta.objects.create(user=cls.usta2_user, fio='Usta Ikki')

        cls.xodim_user = User.objects.create_user(username='x1', rol=User.Rol.XODIM)
        cls.xodim2_user = User.objects.create_user(username='x2', rol=User.Rol.XODIM)
        cls.xodim = Xodim.objects.create(user=cls.xodim_user, fio='Xodim Bir', bolim=cls.bolim)
        cls.xodim2 = Xodim.objects.create(user=cls.xodim2_user, fio='Xodim Ikki', bolim=cls.bolim)

        cls.qurilma = Qurilma.objects.create(
            inventar_raqami='UNI-0001', turi=Qurilma.Turi.PRINTER,
            bolim=cls.bolim, xodim=cls.xodim,
        )
        cls.begona_qurilma = Qurilma.objects.create(
            inventar_raqami='UNI-0002', turi=Qurilma.Turi.MONITOR, bolim=cls.boshqa_bolim,
        )

    def tamir_yarat(self, **maydonlar):
        malumot = {
            'qurilma': self.qurilma, 'xodim': self.xodim,
            'muammo_tavsifi': 'Ishlamayapti',
        }
        malumot.update(maydonlar)
        return TamirYozuvi.objects.create(**malumot)

    def navbatga(self, **maydonlar):
        tamir = self.tamir_yarat(**maydonlar)
        tamir.holat_ozgartir(Holat.QABUL, user=self.operator)
        return tamir


class MurojaatTest(AsosTest):
    def test_xodim_murojaat_yuboradi(self):
        self.client.force_login(self.xodim_user)
        javob = self.client.post(reverse('murojaat_yangi'), {
            'qurilma': self.qurilma.pk,
            'muhimlik': TamirYozuvi.Muhimlik.ODDIY,
            'muammo_tavsifi': 'Qog\'oz tortmayapti',
            'tanlangan_usta': '',
        })
        tamir = TamirYozuvi.objects.get()
        self.assertRedirects(javob, tamir.get_absolute_url())
        self.assertEqual(tamir.holat, Holat.YANGI)
        self.assertEqual(tamir.manba, TamirYozuvi.Manba.SAYT)
        self.assertEqual(tamir.xodim, self.xodim)

    def test_xodim_faqat_oz_bolimi_qurilmasini_tanlay_oladi(self):
        self.client.force_login(self.xodim_user)
        javob = self.client.post(reverse('murojaat_yangi'), {
            'qurilma': self.begona_qurilma.pk,
            'muhimlik': TamirYozuvi.Muhimlik.ODDIY,
            'muammo_tavsifi': 'Test',
        })
        self.assertEqual(javob.status_code, 200)
        self.assertFalse(TamirYozuvi.objects.exists())

    def test_xodim_begona_murojaatni_kora_olmaydi(self):
        tamir = self.tamir_yarat(xodim=self.xodim2)
        self.client.force_login(self.xodim_user)
        self.assertEqual(self.client.get(tamir.get_absolute_url()).status_code, 403)

    def test_operator_qabul_qiladi(self):
        tamir = self.tamir_yarat()
        self.client.force_login(self.operator)
        self.client.post(reverse('murojaat_qabul', args=[tamir.pk]))

        tamir.refresh_from_db()
        self.assertEqual(tamir.holat, Holat.QABUL)
        self.assertIsNotNone(tamir.navbatga_tushgan)

    def test_operator_rad_etadi_sabab_bilan(self):
        tamir = self.tamir_yarat()
        self.client.force_login(self.operator)

        javob = self.client.post(reverse('murojaat_rad', args=[tamir.pk]), {'rad-sabab': ''})
        self.assertEqual(javob.status_code, 200)
        tamir.refresh_from_db()
        self.assertEqual(tamir.holat, Holat.YANGI)

        self.client.post(reverse('murojaat_rad', args=[tamir.pk]),
                         {'rad-sabab': 'Qurilma yaroqsiz'})
        tamir.refresh_from_db()
        self.assertEqual(tamir.holat, Holat.RAD)
        self.assertEqual(tamir.rad_sababi, 'Qurilma yaroqsiz')

    def test_xodim_qabul_qila_olmaydi(self):
        tamir = self.tamir_yarat()
        self.client.force_login(self.xodim_user)
        self.assertEqual(
            self.client.post(reverse('murojaat_qabul', args=[tamir.pk])).status_code, 403,
        )

    def test_rahbariyat_tamirlarga_kira_olmaydi(self):
        self.client.force_login(self.rahbar)
        for url in ['tamir_royxati', 'murojaatlar_navbati', 'navbat', 'tasdiqlash_navbati']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(reverse(url)).status_code, 403)


class NavbatTest(AsosTest):
    def test_usta_navbatdan_ish_oladi(self):
        tamir = self.navbatga()
        self.client.force_login(self.usta_user)
        self.client.post(reverse('ishni_olish', args=[tamir.pk]))

        tamir.refresh_from_db()
        self.assertEqual(tamir.usta, self.usta)
        self.assertEqual(tamir.holat, Holat.TASHXIS)
        self.qurilma.refresh_from_db()
        self.assertEqual(self.qurilma.holati, Qurilma.Holat.TAMIRDA)

    def test_ishni_faqat_bitta_usta_oladi(self):
        tamir = self.navbatga()
        self.client.force_login(self.usta_user)
        self.client.post(reverse('ishni_olish', args=[tamir.pk]))

        self.client.force_login(self.usta2_user)
        self.client.post(reverse('ishni_olish', args=[tamir.pk]))

        tamir.refresh_from_db()
        self.assertEqual(tamir.usta, self.usta)

    def test_soralgan_ish_boshqa_ustaga_tegmaydi(self):
        tamir = self.navbatga(tanlangan_usta=self.usta)
        self.client.force_login(self.usta2_user)
        self.client.post(reverse('ishni_olish', args=[tamir.pk]))

        tamir.refresh_from_db()
        self.assertIsNone(tamir.usta)
        self.assertNotIn(tamir, TamirYozuvi.objects.erkin_navbat())

    def test_javobsiz_soralgan_ish_umumiy_navbatga_tushadi(self):
        tamir = self.navbatga(tanlangan_usta=self.usta)
        TamirYozuvi.objects.filter(pk=tamir.pk).update(
            navbatga_tushgan=timezone.now() - timedelta(days=2),
        )
        self.assertIn(tamir, TamirYozuvi.objects.erkin_navbat())

        self.client.force_login(self.usta2_user)
        self.client.post(reverse('ishni_olish', args=[tamir.pk]))
        tamir.refresh_from_db()
        self.assertEqual(tamir.usta, self.usta2)

    def test_usta_soralgan_ishni_rad_etadi(self):
        tamir = self.navbatga(tanlangan_usta=self.usta)
        self.client.force_login(self.usta_user)
        self.client.post(reverse('soralganni_rad', args=[tamir.pk]))

        tamir.refresh_from_db()
        self.assertIsNone(tamir.tanlangan_usta)
        self.assertIn(tamir, TamirYozuvi.objects.erkin_navbat())

    def test_navbat_shoshilinchni_tepaga_qoyadi(self):
        oddiy = self.navbatga()
        shoshilinch = self.navbatga(muhimlik=TamirYozuvi.Muhimlik.SHOSHILINCH)
        tartib = list(TamirYozuvi.objects.erkin_navbat().navbat_tartibi())
        self.assertEqual(tartib, [shoshilinch, oddiy])

    def test_operator_shoshilinchni_biriktiradi(self):
        tamir = self.navbatga(muhimlik=TamirYozuvi.Muhimlik.SHOSHILINCH)
        self.client.force_login(self.operator)
        self.client.post(reverse('usta_biriktirish', args=[tamir.pk]), {'bir-usta': self.usta.pk})

        tamir.refresh_from_db()
        self.assertEqual(tamir.usta, self.usta)
        self.assertEqual(tamir.holat, Holat.TASHXIS)


class TamirJarayoniTest(AsosTest):
    def setUp(self):
        self.tamir = self.navbatga()
        self.tamir.holat_ozgartir(Holat.TASHXIS, user=self.usta_user, usta=self.usta)

    def test_toliq_jarayon(self):
        self.client.force_login(self.usta_user)
        self.client.post(reverse('ishni_boshlash', args=[self.tamir.pk]))
        self.tamir.refresh_from_db()
        self.assertEqual(self.tamir.holat, Holat.TAMIRDA)

        self.client.post(reverse('ishni_yakunlash', args=[self.tamir.pk]), {
            'yak-bajarilgan_ishlar': 'Kartrij almashtirildi',
            'yak-ehtiyot_qismlar': 'Kartrij 1 dona',
            'yak-xarajat': '150000',
        })
        self.tamir.refresh_from_db()
        self.assertEqual(self.tamir.holat, Holat.TAYYOR)
        self.assertEqual(str(self.tamir.xarajat), '150000.00')

        self.client.force_login(self.operator)
        self.client.post(reverse('topshirish', args=[self.tamir.pk]))
        self.tamir.refresh_from_db()
        self.assertEqual(self.tamir.holat, Holat.TOPSHIRILDI)
        self.assertIsNotNone(self.tamir.topshirilgan_sana)

        self.qurilma.refresh_from_db()
        self.assertEqual(self.qurilma.holati, Qurilma.Holat.ISHLAMOQDA)

    def test_yakunlashda_bajarilgan_ish_majburiy(self):
        self.tamir.holat_ozgartir(Holat.TAMIRDA, user=self.usta_user)
        self.client.force_login(self.usta_user)
        javob = self.client.post(reverse('ishni_yakunlash', args=[self.tamir.pk]),
                                 {'yak-bajarilgan_ishlar': ''})
        self.assertEqual(javob.status_code, 200)
        self.tamir.refresh_from_db()
        self.assertEqual(self.tamir.holat, Holat.TAMIRDA)

    def test_begona_usta_ishni_ozgartira_olmaydi(self):
        self.client.force_login(self.usta2_user)
        self.assertEqual(
            self.client.post(reverse('ishni_boshlash', args=[self.tamir.pk])).status_code, 403,
        )

    def test_notogri_holatdagi_amal_bajarilmaydi(self):
        self.client.force_login(self.operator)
        self.client.post(reverse('topshirish', args=[self.tamir.pk]))
        self.tamir.refresh_from_db()
        self.assertEqual(self.tamir.holat, Holat.TASHXIS)

    def test_status_tarixi_yoziladi(self):
        self.assertEqual(
            [s.yangi_holat for s in self.tamir.status_tarixi.all()],
            [Holat.YANGI, Holat.QABUL, Holat.TASHXIS],
        )


class BaholashTest(AsosTest):
    def setUp(self):
        self.tamir = self.navbatga()
        self.tamir.holat_ozgartir(Holat.TASHXIS, user=self.usta_user, usta=self.usta)
        self.tamir.holat_ozgartir(Holat.TAMIRDA, user=self.usta_user)
        self.tamir.holat_ozgartir(Holat.TAYYOR, user=self.usta_user)
        self.tamir.holat_ozgartir(Holat.TOPSHIRILDI, user=self.operator)

    def test_xodim_baho_beradi(self):
        self.client.force_login(self.xodim_user)
        self.client.post(reverse('baho_berish', args=[self.tamir.pk]),
                         {'baho-baho': '5', 'baho-baho_izoh': 'Rahmat'})
        self.tamir.refresh_from_db()
        self.assertEqual(self.tamir.baho, 5)
        self.assertIsNotNone(self.tamir.baho_sana)
        self.assertFalse(self.tamir.baho_kutilmoqda)

    def test_ikki_marta_baholash_mumkin_emas(self):
        self.client.force_login(self.xodim_user)
        self.client.post(reverse('baho_berish', args=[self.tamir.pk]), {'baho-baho': '5'})
        self.client.post(reverse('baho_berish', args=[self.tamir.pk]), {'baho-baho': '1'})
        self.tamir.refresh_from_db()
        self.assertEqual(self.tamir.baho, 5)

    def test_topshirilmagan_tamirni_baholab_bolmaydi(self):
        boshqa = self.navbatga()
        self.client.force_login(self.xodim_user)
        self.client.post(reverse('baho_berish', args=[boshqa.pk]), {'baho-baho': '5'})
        boshqa.refresh_from_db()
        self.assertIsNone(boshqa.baho)

    def test_begona_xodim_baholay_olmaydi(self):
        self.client.force_login(self.xodim2_user)
        self.assertEqual(
            self.client.post(reverse('baho_berish', args=[self.tamir.pk]),
                             {'baho-baho': '5'}).status_code, 403,
        )


class OziTamirTest(AsosTest):
    def yubor(self):
        self.client.force_login(self.xodim_user)
        self.client.post(reverse('ozi_tamir_yangi'), {
            'qurilma': self.qurilma.pk,
            'muammo_tavsifi': 'Kabel uzilgan edi',
            'bajarilgan_ishlar': 'Kabelni almashtirdim',
            'ehtiyot_qismlar': 'HDMI kabel',
            'xarajat': '40000',
        })
        return TamirYozuvi.objects.get(turi=TamirYozuvi.Turi.OZI)

    def test_xodim_hisobot_yuboradi(self):
        tamir = self.yubor()
        self.assertEqual(tamir.tasdiq_holati, Tasdiq.KUTILMOQDA)
        self.assertEqual(tamir.holat, '')
        self.assertNotIn(tamir, TamirYozuvi.objects.hisobga_kiradi())

    def test_admin_tasdiqlaydi(self):
        tamir = self.yubor()
        self.client.force_login(self.admin)
        self.client.post(reverse('tasdiq_qarori', args=[tamir.pk]),
                         {'tas-qaror': Tasdiq.TASDIQLANDI, 'tas-izoh': ''})

        tamir.refresh_from_db()
        self.assertEqual(tamir.tasdiq_holati, Tasdiq.TASDIQLANDI)
        self.assertEqual(tamir.tasdiqlagan, self.admin)
        self.assertIn(tamir, TamirYozuvi.objects.hisobga_kiradi())

    def test_rad_etishda_izoh_majburiy(self):
        tamir = self.yubor()
        self.client.force_login(self.admin)
        javob = self.client.post(reverse('tasdiq_qarori', args=[tamir.pk]),
                                 {'tas-qaror': Tasdiq.RAD, 'tas-izoh': ''})
        self.assertEqual(javob.status_code, 200)
        tamir.refresh_from_db()
        self.assertEqual(tamir.tasdiq_holati, Tasdiq.KUTILMOQDA)

        self.client.post(reverse('tasdiq_qarori', args=[tamir.pk]),
                         {'tas-qaror': Tasdiq.RAD, 'tas-izoh': 'Hisobot noaniq'})
        tamir.refresh_from_db()
        self.assertEqual(tamir.tasdiq_holati, Tasdiq.RAD)
        self.assertNotIn(tamir, TamirYozuvi.objects.hisobga_kiradi())

    def test_operator_tasdiqlay_olmaydi(self):
        tamir = self.yubor()
        self.client.force_login(self.operator)
        self.assertEqual(
            self.client.post(reverse('tasdiq_qarori', args=[tamir.pk]),
                             {'tas-qaror': Tasdiq.TASDIQLANDI}).status_code, 403,
        )


class SlaVaKunlikTest(AsosTest):
    def test_kechikkanlar_aniqlanadi(self):
        tamir = self.tamir_yarat()
        self.assertEqual(TamirYozuvi.objects.kechikkanlar().count(), 0)

        TamirYozuvi.objects.filter(pk=tamir.pk).update(
            holat_sana=timezone.now() - timedelta(days=5),
        )
        self.assertEqual(TamirYozuvi.objects.kechikkanlar().count(), 1)
        tamir.refresh_from_db()
        self.assertTrue(tamir.kechikkanmi)
        self.assertEqual(tamir.kechikkan_kun, 4)  # YANGI uchun SLA = 1 kun

    def test_kunlik_vazifalar(self):
        # Topshirilgan, ammo baholanmagan ta'mir
        tamir = self.navbatga()
        tamir.holat_ozgartir(Holat.TASHXIS, user=self.usta_user, usta=self.usta)
        tamir.holat_ozgartir(Holat.TAMIRDA, user=self.usta_user)
        tamir.holat_ozgartir(Holat.TAYYOR, user=self.usta_user)
        tamir.holat_ozgartir(Holat.TOPSHIRILDI, user=self.operator)

        # 4 kun oldin topshirilgan → eslatma yuboriladi
        TamirYozuvi.objects.filter(pk=tamir.pk).update(
            topshirilgan_sana=timezone.now() - timedelta(days=4),
        )
        call_command('kunlik_vazifalar', stdout=StringIO())
        tamir.refresh_from_db()
        self.assertTrue(tamir.baho_eslatma_yuborilgan)
        self.assertFalse(tamir.baho_yopilgan)

        # 8 kun oldin topshirilgan → bahosiz yopiladi
        TamirYozuvi.objects.filter(pk=tamir.pk).update(
            topshirilgan_sana=timezone.now() - timedelta(days=8),
        )
        call_command('kunlik_vazifalar', stdout=StringIO())
        tamir.refresh_from_db()
        self.assertTrue(tamir.baho_yopilgan)
        self.assertFalse(tamir.baho_kutilmoqda)

    def test_kunlik_vazifalar_navbatni_tozalaydi(self):
        tamir = self.navbatga(tanlangan_usta=self.usta)
        TamirYozuvi.objects.filter(pk=tamir.pk).update(
            navbatga_tushgan=timezone.now() - timedelta(days=2),
        )
        call_command('kunlik_vazifalar', stdout=StringIO())
        tamir.refresh_from_db()
        self.assertIsNone(tamir.tanlangan_usta)

    def test_quruq_rejim_hech_narsani_ozgartirmaydi(self):
        tamir = self.navbatga(tanlangan_usta=self.usta)
        TamirYozuvi.objects.filter(pk=tamir.pk).update(
            navbatga_tushgan=timezone.now() - timedelta(days=2),
        )
        call_command('kunlik_vazifalar', '--quruq', stdout=StringIO())
        tamir.refresh_from_db()
        self.assertEqual(tamir.tanlangan_usta, self.usta)


class QaytaTamirTest(AsosTest):
    def test_30_kun_ichida_qaytgan_qurilma_belgilanadi(self):
        birinchi = self.navbatga()
        birinchi.holat_ozgartir(Holat.TASHXIS, user=self.usta_user, usta=self.usta)
        birinchi.holat_ozgartir(Holat.TAYYOR, user=self.usta_user)
        birinchi.holat_ozgartir(Holat.TOPSHIRILDI, user=self.operator)

        ikkinchi = self.tamir_yarat(muammo_tavsifi='Yana buzildi')
        self.assertEqual(ikkinchi.qayta_tamir, birinchi)

    def test_eski_tamir_qayta_tamir_hisoblanmaydi(self):
        birinchi = self.navbatga()
        birinchi.holat_ozgartir(Holat.TASHXIS, user=self.usta_user, usta=self.usta)
        birinchi.holat_ozgartir(Holat.TAYYOR, user=self.usta_user)
        birinchi.holat_ozgartir(Holat.TOPSHIRILDI, user=self.operator)
        TamirYozuvi.objects.filter(pk=birinchi.pk).update(
            tugagan_sana=timezone.now() - timedelta(days=40),
        )

        ikkinchi = self.tamir_yarat()
        self.assertIsNone(ikkinchi.qayta_tamir)
