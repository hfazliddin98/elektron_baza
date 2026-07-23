from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Usta


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
