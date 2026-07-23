from django.contrib import admin

from .models import StatusTarix, TamirYozuvi


class StatusTarixInline(admin.TabularInline):
    model = StatusTarix
    extra = 0
    readonly_fields = ('eski_holat', 'yangi_holat', 'ozgartirgan', 'sana')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(TamirYozuvi)
class TamirYozuviAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'qurilma', 'turi', 'holat', 'tasdiq_holati', 'muhimlik',
        'xodim', 'usta', 'qabul_sana', 'baho',
    )
    list_filter = ('turi', 'holat', 'tasdiq_holati', 'muhimlik', 'manba')
    search_fields = ('qurilma__inventar_raqami', 'qurilma__modeli', 'xodim__fio', 'usta__fio')
    date_hierarchy = 'qabul_sana'
    autocomplete_fields = ('qurilma', 'xodim', 'usta', 'tanlangan_usta', 'qayta_tamir')
    list_select_related = ('qurilma', 'xodim', 'usta')
    readonly_fields = ('qabul_sana', 'qayta_tamir')
    inlines = [StatusTarixInline]

    def save_model(self, request, obj, form, change):
        obj._ozgartirgan_user = request.user
        super().save_model(request, obj, form, change)


@admin.register(StatusTarix)
class StatusTarixAdmin(admin.ModelAdmin):
    list_display = ('tamir_yozuvi', 'eski_holat', 'yangi_holat', 'ozgartirgan', 'sana')
    list_filter = ('yangi_holat',)
    date_hierarchy = 'sana'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
