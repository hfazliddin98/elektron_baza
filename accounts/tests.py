from django.test import TestCase
from django.urls import reverse

from .models import AmalTarixi, User, Usta


class RollarTest(TestCase):
    """Rol asosidagi ruxsatlar to'g'ri ishlashini tekshiradi."""

    @classmethod
    def setUpTestData(cls):
        cls.parol = 'Test-parol-123'
        cls.userlar = {}
        for rol in User.Rol.values:
            user = User.objects.create_user(username=f'test_{rol}', password=cls.parol, rol=rol)
            cls.userlar[rol] = user
        Usta.objects.create(user=cls.userlar[User.Rol.USTA], fio='Test Usta')

    def test_kirmagan_foydalanuvchi_panelga_kira_olmaydi(self):
        javob = self.client.get(reverse('dashboard'))
        self.assertRedirects(javob, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_har_bir_rol_uchun_panel_ochiladi(self):
        for rol, user in self.userlar.items():
            with self.subTest(rol=rol):
                self.client.force_login(user)
                javob = self.client.get(reverse('dashboard'))
                self.assertEqual(javob.status_code, 200)
                self.assertContains(javob, user.get_rol_display())

    def test_amal_tarixi_faqat_admin_uchun(self):
        url = reverse('amal_tarixi')
        for rol in [User.Rol.OPERATOR, User.Rol.USTA, User.Rol.XODIM, User.Rol.RAHBARIYAT]:
            with self.subTest(rol=rol):
                self.client.force_login(self.userlar[rol])
                self.assertEqual(self.client.get(url).status_code, 403)

        self.client.force_login(self.userlar[User.Rol.ADMIN])
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_ruxsatsiz_urinish_tarixga_yoziladi(self):
        self.client.force_login(self.userlar[User.Rol.XODIM])
        self.client.get(reverse('amal_tarixi'))
        self.assertTrue(
            AmalTarixi.objects.filter(
                user=self.userlar[User.Rol.XODIM], amal=AmalTarixi.Amal.RUXSATSIZ,
            ).exists()
        )

    def test_superuser_hamma_joyga_kira_oladi(self):
        root = User.objects.create_superuser(
            username='root', password=self.parol, rol=User.Rol.XODIM,
        )
        self.client.force_login(root)
        self.assertEqual(self.client.get(reverse('amal_tarixi')).status_code, 200)


class KirishChiqishTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parol = 'Test-parol-123'
        cls.user = User.objects.create_user(
            username='xodim_test', password=cls.parol, rol=User.Rol.XODIM,
        )

    def test_kirish_tarixga_yoziladi(self):
        self.client.post(reverse('login'), {'username': 'xodim_test', 'password': self.parol})
        self.assertTrue(
            AmalTarixi.objects.filter(user=self.user, amal=AmalTarixi.Amal.KIRISH).exists()
        )

    def test_notogri_parol_tarixga_yoziladi(self):
        javob = self.client.post(
            reverse('login'), {'username': 'xodim_test', 'password': 'xato-parol'},
        )
        self.assertEqual(javob.status_code, 200)
        self.assertTrue(AmalTarixi.objects.filter(amal=AmalTarixi.Amal.KIRISH_XATO).exists())

    def test_chiqish(self):
        self.client.force_login(self.user)
        javob = self.client.post(reverse('logout'))
        self.assertRedirects(javob, reverse('login'))
        self.assertTrue(
            AmalTarixi.objects.filter(user=self.user, amal=AmalTarixi.Amal.CHIQISH).exists()
        )

    def test_parol_ozgartirish(self):
        self.client.force_login(self.user)
        javob = self.client.post(reverse('parol_ozgartirish'), {
            'old_password': self.parol,
            'new_password1': 'Yangi-parol-456',
            'new_password2': 'Yangi-parol-456',
        })
        self.assertRedirects(javob, reverse('parol_tayyor'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Yangi-parol-456'))
        self.assertTrue(
            AmalTarixi.objects.filter(user=self.user, amal=AmalTarixi.Amal.PAROL).exists()
        )

    def test_bosh_sahifa_kirgan_foydalanuvchini_panelga_yonaltiradi(self):
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(reverse('home')), reverse('dashboard'))
