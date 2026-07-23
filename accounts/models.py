from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Tizim foydalanuvchisi — rol asosida huquqlar beriladi (5-bosqich)."""

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
