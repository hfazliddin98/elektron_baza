from django.conf import settings
from django.db import models


class Bolim(models.Model):
    nomi = models.CharField('Nomi', max_length=200, unique=True)
    bino = models.CharField('Bino', max_length=100, blank=True)
    xona = models.CharField('Xona', max_length=50, blank=True)

    class Meta:
        verbose_name = "Bo'lim"
        verbose_name_plural = "Bo'limlar"
        ordering = ['nomi']

    def __str__(self):
        return self.nomi


class Xodim(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Foydalanuvchi (login)',
    )
    fio = models.CharField('F.I.Sh.', max_length=150)
    bolim = models.ForeignKey(
        Bolim, on_delete=models.PROTECT, related_name='xodimlar', verbose_name="Bo'lim",
    )
    lavozimi = models.CharField('Lavozimi', max_length=150, blank=True)
    telefon = models.CharField('Telefon', max_length=20, blank=True)
    telegram_id = models.BigIntegerField('Telegram ID', unique=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Xodim'
        verbose_name_plural = 'Xodimlar'
        ordering = ['fio']

    def __str__(self):
        return self.fio


class Qurilma(models.Model):
    class Turi(models.TextChoices):
        KOMPYUTER = 'kompyuter', 'Kompyuter'
        MONITOR = 'monitor', 'Monitor'
        PRINTER = 'printer', 'Printer'
        MFU = 'mfu', 'MFU'
        PROYEKTOR = 'proyektor', 'Proyektor'
        SKANER = 'skaner', 'Skaner'
        UPS = 'ups', 'UPS'
        BOSHQA = 'boshqa', 'Boshqa'

    class Holat(models.TextChoices):
        ISHLAMOQDA = 'ishlamoqda', 'Ishlamoqda'
        TAMIRDA = 'tamirda', "Ta'mirda"
        YAROQSIZ = 'yaroqsiz', 'Yaroqsiz'

    inventar_raqami = models.CharField('Inventar raqami', max_length=50, unique=True)
    turi = models.CharField('Turi', max_length=20, choices=Turi.choices)
    modeli = models.CharField('Modeli', max_length=200, blank=True)
    seriya_raqami = models.CharField('Seriya raqami', max_length=100, blank=True)
    bolim = models.ForeignKey(
        Bolim, on_delete=models.PROTECT, related_name='qurilmalar', verbose_name="Bo'lim",
    )
    xodim = models.ForeignKey(
        Xodim, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='qurilmalar', verbose_name='Biriktirilgan xodim',
    )
    holati = models.CharField('Holati', max_length=20, choices=Holat.choices, default=Holat.ISHLAMOQDA)
    olingan_sana = models.DateField('Olingan sana', null=True, blank=True)
    # QR-kod rasmi 6-bosqichda avtomatik generatsiya qilinadi
    qr_kod = models.ImageField('QR-kod', upload_to='qr_kodlar/', blank=True)

    class Meta:
        verbose_name = 'Qurilma'
        verbose_name_plural = 'Qurilmalar'
        ordering = ['inventar_raqami']

    def __str__(self):
        return f'{self.inventar_raqami} — {self.get_turi_display()} {self.modeli}'.strip()
