from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import Case, IntegerField, Q, Value, When
from django.urls import reverse
from django.utils import timezone


class TamirQuerySet(models.QuerySet):
    def navbatdagi(self):
        """Qabul qilingan, lekin hali usta olmagan ta'mirlar."""
        return self.filter(holat=self.model.Holat.QABUL, usta__isnull=True)

    def erkin_navbat(self):
        """Har qanday usta olishi mumkin bo'lganlar.

        Xodim usta tanlagan bo'lsa, o'sha usta uchun belgilangan muddat
        (1 ish kuni) o'tgandan keyingina umumiy navbatga tushadi.
        """
        chegara = timezone.now() - timedelta(days=self.model.TANLANGAN_USTA_KUN)
        return self.navbatdagi().filter(
            Q(tanlangan_usta__isnull=True) | Q(navbatga_tushgan__lt=chegara)
        )

    def ustaga_soralgan(self, usta):
        """Xodim shaxsan shu ustadan so'ragan, hali javobsiz ta'mirlar."""
        chegara = timezone.now() - timedelta(days=self.model.TANLANGAN_USTA_KUN)
        return self.navbatdagi().filter(tanlangan_usta=usta, navbatga_tushgan__gte=chegara)

    def navbat_tartibi(self):
        """Shoshilinchlar tepada, keyin eng eskisi birinchi."""
        return self.annotate(
            _muhim=Case(
                When(muhimlik=self.model.Muhimlik.SHOSHILINCH, then=Value(0)),
                default=Value(1), output_field=IntegerField(),
            )
        ).order_by('_muhim', 'navbatga_tushgan', 'pk')

    def kechikkanlar(self):
        """SLA muddati o'tib ketgan ta'mirlar."""
        endi = timezone.now()
        shart = Q(pk__in=[])
        for holat, kun in self.model.SLA_KUN.items():
            shart |= Q(holat=holat, holat_sana__lt=endi - timedelta(days=kun))
        return self.filter(shart)

    def jarayondagi(self):
        return self.filter(holat__in=self.model.JARAYONDAGI_HOLATLAR)

    def usta_tamirlari(self):
        return self.filter(turi=self.model.Turi.USTA)

    def hisobga_kiradi(self):
        """Hisobotlarda ko'rinadigan yozuvlar: usta ta'mirlari va
        tasdiqlangan o'zi-ta'mirlar (rad etilganlar hisobga olinmaydi)."""
        return self.filter(
            Q(turi=self.model.Turi.USTA)
            | Q(turi=self.model.Turi.OZI, tasdiq_holati=self.model.Tasdiq.TASDIQLANDI)
        )


class TamirYozuvi(models.Model):
    """Ta'mirlash yozuvi: usta ta'miri ham, xodim o'zi ta'mirlagani ham shu jadvalda.

    Holat o'zgarishlari StatusTarix'ga avtomatik yoziladi. Status'ni
    `holat_ozgartir(yangi_holat, user)` orqali o'zgartirish tavsiya etiladi —
    shunda tarixda kim o'zgartirgani ham saqlanadi.
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

    JARAYONDAGI_HOLATLAR = [Holat.YANGI, Holat.QABUL, Holat.TASHXIS, Holat.TAMIRDA, Holat.TAYYOR]

    # Har bir holat uchun ruxsat etilgan maksimal muddat (kun) — SLA nazorati
    SLA_KUN = {
        Holat.YANGI: 1,
        Holat.QABUL: 2,
        Holat.TASHXIS: 2,
        Holat.TAMIRDA: 5,
        Holat.TAYYOR: 3,
    }

    QAYTA_TAMIR_KUN = 30       # shu muddat ichida qaytsa — qayta ta'mir
    NAVBAT_HAJMI = 10          # usta navbatning eng eski 10 tasini ko'radi
    TANLANGAN_USTA_KUN = 1     # tanlangan usta javob berishi kerak bo'lgan muddat
    BAHO_ESLATMA_KUN = 3       # shu kundan keyin baholash eslatiladi
    BAHO_YOPISH_KUN = 7        # shu kundan keyin bahosiz yopiladi

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
    navbatga_tushgan = models.DateTimeField('Navbatga tushgan sana', null=True, blank=True)
    boshlangan_sana = models.DateTimeField('Boshlangan sana', null=True, blank=True)
    tugagan_sana = models.DateTimeField('Tugagan sana', null=True, blank=True)
    topshirilgan_sana = models.DateTimeField('Topshirilgan sana', null=True, blank=True)
    holat_sana = models.DateTimeField('Joriy holat sanasi', null=True, blank=True)
    bajarilgan_ishlar = models.TextField('Bajarilgan ishlar', blank=True)
    ehtiyot_qismlar = models.TextField('Ehtiyot qismlar', blank=True)
    xarajat = models.DecimalField("Xarajat (so'm)", max_digits=12, decimal_places=2, default=0)
    holat = models.CharField('Holat', max_length=15, choices=Holat.choices, default=Holat.YANGI, blank=True)
    rad_sababi = models.TextField('Rad etish sababi', blank=True)
    tasdiq_holati = models.CharField(
        'Tasdiq holati', max_length=15, choices=Tasdiq.choices, blank=True, default='',
        help_text="Faqat \"o'zi ta'mirlagan\" yozuvlar uchun",
    )
    tasdiqlagan = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tasdiqlagan_tamirlar', verbose_name='Tasdiqlagan/rad etgan',
    )
    tasdiq_izohi = models.TextField('Tasdiq izohi', blank=True)
    tasdiq_sana = models.DateTimeField('Tasdiq sanasi', null=True, blank=True)
    qayta_tamir = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='qayta_tamirlar', verbose_name="Qayta ta'mir (oldingi ta'mir)",
    )
    baho = models.PositiveSmallIntegerField(
        'Baho', null=True, blank=True, choices=[(i, str(i)) for i in range(1, 6)],
    )
    baho_izoh = models.TextField('Baho izohi', blank=True)
    baho_sana = models.DateTimeField('Baho sanasi', null=True, blank=True)
    baho_eslatma_yuborilgan = models.BooleanField('Baho eslatmasi yuborilgan', default=False)
    baho_yopilgan = models.BooleanField('Bahosiz yopilgan', default=False)

    objects = TamirQuerySet.as_manager()

    class Meta:
        verbose_name = "Ta'mir yozuvi"
        verbose_name_plural = "Ta'mir yozuvlari"
        ordering = ['-qabul_sana']
        indexes = [
            models.Index(fields=['holat', 'holat_sana']),
            models.Index(fields=['turi', 'tasdiq_holati']),
        ]

    def __str__(self):
        return f'#{self.pk} — {self.qurilma}'

    def get_absolute_url(self):
        return reverse('tamir_batafsil', args=[self.pk])

    # --- Ko'rinish uchun yordamchilar ---

    @property
    def ozi_tamiri(self):
        return self.turi == self.Turi.OZI

    @property
    def holat_nomi(self):
        if self.ozi_tamiri:
            return self.get_tasdiq_holati_display()
        return self.get_holat_display()

    @property
    def holat_rangi(self):
        if self.ozi_tamiri:
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
    def sla_kuni(self):
        return self.SLA_KUN.get(self.holat)

    @property
    def kechikkan_kun(self):
        """Joriy holatda ruxsat etilgan muddatdan necha kun oshgani (0 — kechikmagan)."""
        if not self.sla_kuni or not self.holat_sana:
            return 0
        otgan = (timezone.now() - self.holat_sana).days
        return max(0, otgan - self.sla_kuni)

    @property
    def kechikkanmi(self):
        return self.kechikkan_kun > 0

    @property
    def baho_kutilmoqda(self):
        return (
            not self.ozi_tamiri
            and self.holat == self.Holat.TOPSHIRILDI
            and self.baho is None
            and not self.baho_yopilgan
        )

    @property
    def tamir_muddati_kun(self):
        """Qabuldan topshirishgacha ketgan kun (tugallanmagan bo'lsa None)."""
        if not self.topshirilgan_sana:
            return None
        return (self.topshirilgan_sana - self.qabul_sana).days

    # --- Saqlash mantig'i ---

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
            endi = timezone.now()
            self.holat_sana = endi
            if self.holat == self.Holat.QABUL and not self.navbatga_tushgan:
                self.navbatga_tushgan = endi
            if self.holat == self.Holat.TASHXIS and not self.boshlangan_sana:
                self.boshlangan_sana = endi
            if self.holat == self.Holat.TAYYOR and not self.tugagan_sana:
                self.tugagan_sana = endi
            if self.holat == self.Holat.TOPSHIRILDI and not self.topshirilgan_sana:
                self.topshirilgan_sana = endi

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

    def holat_ozgartir(self, yangi_holat, user=None, **maydonlar):
        """Holatni o'zgartiradi va tarixga kim o'zgartirganini yozadi."""
        self._ozgartirgan_user = user
        for nom, qiymat in maydonlar.items():
            setattr(self, nom, qiymat)
        self.holat = yangi_holat
        self.save()

    def _qayta_tamirni_aniqlash(self):
        """Shu qurilma yaqinda ta'mirdan chiqqan bo'lsa — qayta ta'mir deb belgilanadi."""
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

    @property
    def nomi(self):
        """Holat kodini o'qiladigan nomga aylantiradi."""
        xarita = dict(TamirYozuvi.Holat.choices) | dict(TamirYozuvi.Tasdiq.choices)
        return xarita.get(self.yangi_holat, self.yangi_holat)
