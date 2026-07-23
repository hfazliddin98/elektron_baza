from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Tizim foydalanuvchisi — rol asosida huquqlar beriladi."""

    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        OPERATOR = 'operator', 'Operator'
        USTA = 'usta', 'Usta'
        XODIM = 'xodim', 'Xodim'
        RAHBARIYAT = 'rahbariyat', 'Rahbariyat'

    rol = models.CharField('Rol', max_length=20, choices=Rol.choices, default=Rol.XODIM)

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    @property
    def is_admin(self):
        return self.rol == self.Rol.ADMIN or self.is_superuser

    @property
    def is_operator(self):
        return self.rol == self.Rol.OPERATOR

    @property
    def is_usta(self):
        return self.rol == self.Rol.USTA

    @property
    def is_xodim(self):
        return self.rol == self.Rol.XODIM

    @property
    def is_rahbariyat(self):
        return self.rol == self.Rol.RAHBARIYAT

    @property
    def usta_profili(self):
        """Usta yozuvi (bog'lanmagan bo'lsa None)."""
        return getattr(self, 'usta', None)

    @property
    def xodim_profili(self):
        """Xodim yozuvi (bog'lanmagan bo'lsa None)."""
        return getattr(self, 'xodim', None)


class Usta(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Foydalanuvchi (login)',
    )
    fio = models.CharField('F.I.Sh.', max_length=150)
    mutaxassisligi = models.CharField('Mutaxassisligi', max_length=150, blank=True)
    telefon = models.CharField('Telefon', max_length=20, blank=True)
    faol = models.BooleanField('Faol', default=True)

    class Meta:
        verbose_name = 'Usta'
        verbose_name_plural = 'Ustalar'
        ordering = ['fio']

    def __str__(self):
        return self.fio


class AmalTarixi(models.Model):
    """Audit log: kim, qachon, nima qildi."""

    class Amal(models.TextChoices):
        KIRISH = 'kirish', 'Tizimga kirdi'
        CHIQISH = 'chiqish', 'Tizimdan chiqdi'
        KIRISH_XATO = 'kirish_xato', 'Kirishda xato'
        PAROL = 'parol', "Parolni o'zgartirdi"
        YARATISH = 'yaratish', 'Yaratdi'
        TAHRIRLASH = 'tahrirlash', 'Tahrirladi'
        OCHIRISH = 'ochirish', "O'chirdi"
        HOLAT = 'holat', "Holatni o'zgartirdi"
        TASDIQLASH = 'tasdiqlash', 'Tasdiqladi'
        RAD = 'rad', 'Rad etdi'
        RUXSATSIZ = 'ruxsatsiz', 'Ruxsatsiz urinish'

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='amallari', verbose_name='Foydalanuvchi',
    )
    amal = models.CharField('Amal', max_length=20, choices=Amal.choices)
    obyekt = models.CharField('Obyekt', max_length=200, blank=True)
    izoh = models.TextField('Izoh', blank=True)
    ip = models.GenericIPAddressField('IP manzil', null=True, blank=True)
    sana = models.DateTimeField('Sana', auto_now_add=True)

    class Meta:
        verbose_name = 'Amal tarixi'
        verbose_name_plural = 'Amallar tarixi'
        ordering = ['-sana']
        indexes = [models.Index(fields=['-sana'])]

    def __str__(self):
        return f'{self.user or "—"}: {self.get_amal_display()} {self.obyekt}'.strip()
