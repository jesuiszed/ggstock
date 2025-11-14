from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')
    
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'Aucun profil'
    get_role.short_description = 'Rôle'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'date_creation')
    list_filter = ('role', 'date_creation')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('date_creation',)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
