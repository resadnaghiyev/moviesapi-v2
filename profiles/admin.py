from django.contrib import admin

from .models import Profile, Watchlist, WatchlistTime


class WatchlistTimeAdmin(admin.TabularInline):
    model = WatchlistTime


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    # list_display = ("user", "movie",)
    inlines = [WatchlistTimeAdmin]


admin.site.register(Profile)
