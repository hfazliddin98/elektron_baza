from django.contrib import admin

from .models import Bolim, Qurilma, Xodim


@admin.register(Bolim)
class BolimAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'bino', 'xona')
    search_fields = ('nomi',)


@admin.register(Xodim)
class XodimAdmin(admin.ModelAdmin):
    list_display = ('fio', 'bolim', 'lavozimi', 'telefon', 'telegram_id', 'user')
    list_filter = ('bolim',)
    search_fields = ('fio', 'telefon', 'lavozimi')
    autocomplete_fields = ('user', 'bolim')


@admin.register(Qurilma)
class QurilmaAdmin(admin.ModelAdmin):
    list_display = ('inventar_raqami', 'turi', 'modeli', 'bolim', 'xodim', 'holati', 'olingan_sana')
    list_filter = ('turi', 'holati', 'bolim')
    search_fields = ('inventar_raqami', 'modeli', 'seriya_raqami')
    autocomplete_fields = ('bolim', 'xodim')
    list_select_related = ('bolim', 'xodim')
