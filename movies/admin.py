from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import (Director, Genre, Certificate,
                     ImdbRating, StreamingService, Production,
                     Movie, MovieShots, RatingStar, Review, Rating)


class MovieAdminForm(forms.ModelForm):
    """Ckeditor widgetin formasi"""
    description = forms.CharField(label="Haqqında", widget=CKEditorUploadingWidget())

    class Meta:
        model = Movie
        fields = '__all__'


class ReviewInline(admin.TabularInline):
    """Film səhifəsindəki rəylər"""
    model = Review
    extra = 0
    readonly_fields = ("user", "parent", "movie", "get_likes", "get_dislikes")
    fieldsets = (
        (None, {
            "fields": ("content", "spoiler", "get_likes", "get_dislikes", "user", "parent")
        }),
    )

    def get_likes(self, obj):
        return obj.likes.count()

    def get_dislikes(self, obj):
        return obj.unlikes.count()

    get_likes.short_description = "Like"
    get_dislikes.short_description = "Dislike"


class MovieShotsInline(admin.TabularInline):
    """Film səhifəsindəki sekiller"""
    model = MovieShots
    extra = 0
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="150" height="90"')

    get_image.short_description = "Şəkil"


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Kino"""
    list_display = ("title", "movie_slug", "draft")
    list_filter = ("genres", "year")
    list_editable = ("draft",)
    search_fields = ("title", )
    actions = ["publish", "unpublish"]
    readonly_fields = ("get_image",)
    inlines = [MovieShotsInline, ReviewInline]
    form = MovieAdminForm
    save_on_top = True
    save_as = True
    fieldsets = (
        (None, {
            "fields": (("title", "tagline"), ("certificate", "trailer"),)
        }),
        (None, {
            "fields": ("description", ("image", "get_image"))
        }),
        (None, {
            "fields": (("year", "country"), ("premiere", "runtime"))
        }),
        (None, {
            "fields": (("directors", "genres"),)
        }),
        (None, {
            "fields": (("production", "streaming"),)
        }),
        (None, {
            "fields": (("budget", "box_office", "imdb"),)
        }),
        ("Options", {
            "fields": (("movie_slug", "draft"),)
        }),
    )

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="100" height="150"')

    def unpublish(self, request, queryset):
        """Nəşri dayandırmaq"""
        row_update = queryset.update(draft=True)
        if row_update == 1:
            message_bit = "1 kino qaralamaya salındı"
        else:
            message_bit = f"{row_update} kino qaralamaya salındı"
        self.message_user(request, f"{message_bit}")

    def publish(self, request, queryset):
        """Nəşr etmək"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message_bit = "1 kino qaralamadan çıxarıldı"
        else:
            message_bit = f"{row_update} kino qaralamadan çıxarıldı"
        self.message_user(request, f"{message_bit}")

    publish.short_description = "Nəşr etmək"
    publish.allowed_permissions = ('change', )

    unpublish.short_description = "Nəşri dayandırmaq"
    unpublish.allowed_permissions = ('change',)

    get_image.short_description = "Afişa"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Kinoların rəyləri"""
    list_display = ("id", "user", "movie", "spoiler")
    list_display_links = ('id', 'user',)
    list_editable = ("spoiler",)
    # readonly_fields = ("user", "parent", "movie")


@ admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Janr"""
    list_display = ("name", "url", "image")  # , "get_image")
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="50" height="50"')

    get_image.short_description = "Icon"


@ admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    """Rejissor"""
    list_display = ("name",)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Reytinq"""
    list_display = ("star", "movie", "user")
    list_display_links = ("star", "movie")


@ admin.register(MovieShots)
class MovieShotsAdmin(admin.ModelAdmin):
    """Kinodan şəkillər"""
    list_display = ("title", "movie", "get_image")
    list_display_links = ("title", "movie")
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="150" height="90"')

    get_image.short_description = "Şəkil"


admin.site.register(ImdbRating)
admin.site.register(RatingStar)
admin.site.register(Production)
admin.site.register(Certificate)
admin.site.register(StreamingService)

admin.site.site_title = "Django Movies Api"
admin.site.site_header = "Django Movies Api"
