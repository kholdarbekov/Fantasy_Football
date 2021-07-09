from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from .models import User, Team, Player, TransferList, TransferHistory


class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ('email', )

    fieldsets = (
        (None, {'fields': ('email', 'password', 'role')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Soccer'), {'fields': ('team', )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'team', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email')


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'value')


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'age', 'price', 'team')


class TransferListAdmin(admin.ModelAdmin):
    list_display = ('player', 'asking_price')


class TransferHistoryAdmin(admin.ModelAdmin):
    list_display = ('player', 'sell_price', 'sell_team', 'buy_team', 'time')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(TransferList, TransferListAdmin)
admin.site.register(TransferHistory, TransferHistoryAdmin)
