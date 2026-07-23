from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class TamirYozuvi(models.Model):
    """Ta'mirlash yozuvi: usta ta'miri ham, xodim o'zi ta'mirlagani ham shu jadvalda.

    Holat o'zgarishlari StatusTarix'ga avtomatik yoziladi. View/admin status
    o'zgartirishdan oldin `_ozgartirgan_user` atributini qo'yishi kerak
    (yoki `holat_ozgartir()` yordamchisidan foydalanadi).
    """

    class Turi(models.TextChoices):
        USTA = 'usta', "Usta ta'miri"
        OZI = 'ozi', "O'zi ta'mirlagan"

    class Manba(models.TextChoices):
        OPERATOR = 'operator', 'Operator'
        SAYT = 'sayt', 'Sayt'
        BOT = 'bot', 'Telegram bot'

    class Muhimlik(models.TextChoices):
        ODDIY = 'oddiy', 'Oddiy'
        SHOSHILINCH = 'shoshilinch', 'Shoshilinch'

    class Holat(models.TextChoices):
        YANGI = 'yangi', 'Yangi murojaat'
        QABUL = 'qabul', 'Qabul qilindi (navbatda)'
        TASHXIS = 'tashxis', 'Tashxisda'
        TAMIRDA = 'tamirda', "Ta'mirda"
        TAYYOR = 'tayyor', 'Tayyor'
        TOPSHIRILDI = 'topshirildi', 'Topshirildi'
        RAD = 'rad', 'Rad etildi'

    class Tasdiq(models.TextChoices):
        KUTILMOQDA = 'kutilmoqda', 'Tasdiq kutilmoqda'
        TASDIQLANDI = 'tasdiqlandi', 'Tasdiqlandi'
        RAD = 'rad', 'Rad etildi'

    QAYTA_TAMIR_KUN = 30
    NAVBAT_HAJMI = 10

    qurilma = models.ForeignKey(
        'devices.Qurilma', on_delete=models.PROTECT,
        related_name='tamirlar', verbose_name='Qurilma',
    )
    xodim = models.ForeignKey(
        'devices.Xodim', on_delete=models.PROTECT,
        related_name='tamirlar', verbose_name='Murojaat qilgan xodim',
    )
    turi = models.CharField('Turi', max_length=10, choices=Turi.choices, default=Turi.USTA)
    manba = models.CharField('Manba', max_length=10, choices=Manba.choices, default=Manba.OPERATOR)
    muhimlik = models.CharField('Muhimlik', max_length=15, choices=Muhimlik.choices, default=Muhimlik.ODDIY)
    muammo_tavsifi = models.TextField('Muammo tavsifi')
    rasm = models.ImageField('Rasm', upload_to='tamir_rasmlar/', blank=True)
    usta = models.ForeignKey(
        'accounts.Usta', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tamirlar', verbose_name='Usta',
    )
    tanlangan_usta = models.ForeignKey(
        'accounts.Usta', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='soralgan_tamirlar', verbose_name='Xodim tanlagan usta',
    )
    qabul_sana = models.DateTimeField('Qabul sanasi', auto_now_add=True)
    boshlangan_sana = models.DateTimeField('Boshlangan sana', null=True, blank=True)
    tugagan_sana = models.DateTimeField('Tugagan sana', null=True, blank=True)
    bajarilgan_ishlar = models.TextField('Bajarilgan ishlar', blank=True)
    ehtiyot_qismlar = models.TextField('Ehtiyot qismlar', blank=True)
    xarajat = models.DecimalField('Xarajat (so\'m)', max_digits=12, decimal_places=2, default=0)
    holat = models.CharField('Holat', max_length=15, choices=Holat.choices, default=Holat.YANGI, blank=True)
    tasdiq_holati = models.CharField(
        'Tasdiq holati', max_length=15, choices=Tasdiq.choices, blank=True, default='',
        help_text="Faqat \"o'zi ta'mirlagan\" yozuvlar uchun",
    )
    qayta_tamir = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='qayta_tamirlar', verbose_name="Qayta ta'mir (oldingi ta'mir)",
    )
    baho = models.PositiveSmallIntegerField(
        'Baho', null=True, blank=True, choices=[(i, str(i)) for i in range(1, 6)],
    )
    baho_izoh = models.TextField('Baho izohi', blank=True)

    class Meta:
        verbose_name = "Ta'mir yozuvi"
        verbose_name_plural = "Ta'mir yozuvlari"
        ordering = ['-qabul_sana']

    def __str__(self):
        return f'#{self.pk} — {self.qurilma}'

    @property
    def holat_rangi(self):
        if self.turi == self.Turi.OZI:
            return {
                self.Tasdiq.KUTILMOQDA: 'warning',
                self.Tasdiq.TASDIQLANDI: 'success',
                self.Tasdiq.RAD: 'danger',
            }.get(self.tasdiq_holati, 'secondary')
        return {
            self.Holat.YANGI: 'warning',
            self.Holat.QABUL: 'info',
            self.Holat.TASHXIS: 'primary',
            self.Holat.TAMIRDA: 'primary',
            self.Holat.TAYYOR: 'success',
            self.Holat.TOPSHIRILDI: 'secondary',
            self.Holat.RAD: 'danger',
        }.get(self.holat, 'secondary')

    @property
    def holat_nomi(self):
        if self.turi == self.Turi.OZI:
            return self.get_tasdiq_holati_display()
        return self.get_holat_display()

    def save(self, *args, **kwargs):
        yangi_yozuv = self.pk is None
        eski_holat = eski_tasdiq = ''

        if yangi_yozuv:
            if self.turi == self.Turi.OZI:
                self.holat = ''
                if not self.tasdiq_holati:
                    self.tasdiq_holati = self.Tasdiq.KUTILMOQDA
            else:
                self.tasdiq_holati = ''
                if not self.holat:
                    self.holat = self.Holat.YANGI
                self._qayta_tamirni_aniqlash()
        else:
            eski_holat, eski_tasdiq = (
                type(self).objects.filter(pk=self.pk)
                .values_list('holat', 'tasdiq_holati').first()
            )

        holat_ozgardi = self.holat != eski_holat
        if holat_ozgardi:
            if self.holat == self.Holat.TASHXIS and not self.boshlangan_sana:
                self.boshlangan_sana = timezone.now()
            if self.holat == self.Holat.TAYYOR and not self.tugagan_sana:
                self.tugagan_sana = timezone.now()

        super().save(*args, **kwargs)

        user = getattr(self, '_ozgartirgan_user', None)
        if holat_ozgardi:
            StatusTarix.objects.create(
                tamir_yozuvi=self, eski_holat=eski_holat,
                yangi_holat=self.holat, ozgartirgan=user,
            )
            self._qurilma_holatini_yangilash()
        if self.tasdiq_holati != eski_tasdiq:
            StatusTarix.objects.create(
                tamir_yozuvi=self, eski_holat=eski_tasdiq,
                yangi_holat=self.tasdiq_holati, ozgartirgan=user,
            )

    def holat_ozgartir(self, yangi_holat, user=None):
        self._ozgartirgan_user = user
        self.holat = yangi_holat
        self.save()

    def _qayta_tamirni_aniqlash(self):
        """Shu qurilma 30 kun ichida ta'mirdan chiqqan bo'lsa — qayta ta'mir."""
        chegara = timezone.now() - timedelta(days=self.QAYTA_TAMIR_KUN)
        self.qayta_tamir = (
            type(self).objects
            .filter(qurilma=self.qurilma, holat=self.Holat.TOPSHIRILDI, tugagan_sana__gte=chegara)
            .order_by('-tugagan_sana').first()
        )

    def _qurilma_holatini_yangilash(self):
        from devices.models import Qurilma

        if self.holat in (self.Holat.TASHXIS, self.Holat.TAMIRDA, self.Holat.TAYYOR):
            yangi = Qurilma.Holat.TAMIRDA
        elif self.holat == self.Holat.TOPSHIRILDI:
            yangi = Qurilma.Holat.ISHLAMOQDA
        else:
            return
        if self.qurilma.holati not in (yangi, Qurilma.Holat.YAROQSIZ):
            self.qurilma.holati = yangi
            self.qurilma.save(update_fields=['holati'])


class StatusTarix(models.Model):
    tamir_yozuvi = models.ForeignKey(
        TamirYozuvi, on_delete=models.CASCADE,
        related_name='status_tarixi', verbose_name="Ta'mir yozuvi",
    )
    eski_holat = models.CharField('Eski holat', max_length=15, blank=True)
    yangi_holat = models.CharField('Yangi holat', max_length=15)
    ozgartirgan = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="O'zgartirgan",
    )
    sana = models.DateTimeField('Sana', auto_now_add=True)

    class Meta:
        verbose_name = 'Status tarixi'
        verbose_name_plural = 'Status tarixi'
        ordering = ['sana']

    def __str__(self):
        return f'{self.tamir_yozuvi_id}: {self.eski_holat or "—"} → {self.yangi_holat}'
