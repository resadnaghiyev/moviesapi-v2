from django.contrib import admin

from .models import User


# admin.site.register(User)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Userler"""
    readonly_fields = ("password",)
