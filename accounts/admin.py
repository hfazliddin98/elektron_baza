from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AmalTarixi, User, Usta


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (('Rol', {'fields': ('rol',)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (('Rol', {'fields': ('rol',)}),)
    list_display = ('username', 'first_name', 'last_name', 'rol', 'is_active')
    list_filter = ('rol', 'is_active', 'is_staff')


@admin.register(Usta)
class UstaAdmin(admin.ModelAdmin):
    list_display = ('fio', 'mutaxassisligi', 'telefon', 'faol', 'user')
    list_filter = ('faol',)
    search_fields = ('fio', 'telefon')
    autocomplete_fields = ('user',)


@admin.register(AmalTarixi)
class AmalTarixiAdmin(admin.ModelAdmin):
    list_display = ('sana', 'user', 'amal', 'obyekt', 'ip')
    list_filter = ('amal',)
    search_fields = ('user__username', 'obyekt', 'izoh')
    date_hierarchy = 'sana'
    list_select_related = ('user',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
