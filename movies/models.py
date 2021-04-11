from django.db import models
from datetime import date
from django.urls import reverse
from django.conf import settings


User = settings.AUTH_USER_MODEL


class Director(models.Model):
    """Rejissor"""
    name = models.CharField("Ad Soyad", max_length=100)
    # birthday = models.DateField("Doğum tarixi", default=date.today)
    # description = models.TextField("Haqqında", default="", null=True, blank=True)
    # image = models.ImageField("Şəkil", upload_to="actors/", null=True, blank=True)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #    return reverse('director_detail', kwargs={"slug": self.name})

    class Meta:
        verbose_name = "Rejissor"
        verbose_name_plural = "Rejissorlar"


class Genre(models.Model):
    """Janr"""
    name = models.CharField("Ad", max_length=100)
    image = models.ImageField("Icon", upload_to="genre_icons/", null=True, blank=True)
    url = models.SlugField(max_length=160, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Janr"
        verbose_name_plural = "Janrlar"


class Certificate(models.Model):
    """Sertifikat"""
    rated = models.CharField(max_length=50)
    url = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.rated

    class Meta:
        verbose_name = "Sertifikat"
        verbose_name_plural = "Sertifikatlar"


class ImdbRating(models.Model):
    """IMDb Reytinqi"""
    point = models.FloatField(null=True, blank=True)
    votes = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'Point: {self.point} -- Votes: {self.votes}'

    class Meta:
        ordering = ['-point', '-votes']
        verbose_name = "IMDb Reytinqi"
        verbose_name_plural = "IMDb Reytinqləri"


class StreamingService(models.Model):
    """Yayım Platforması"""
    name = models.CharField(max_length=50)
    image = models.ImageField("Logo", upload_to="platform_logos/", null=True, blank=True)
    website = models.URLField("Sayt", max_length=2000, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Yayım Platforması"
        verbose_name_plural = "Yayım Platformaları"


class Production(models.Model):
    """İstehsal Şirkəti"""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "İstehsal Şirkəti"
        verbose_name_plural = "İstehsal Şirkətləri"


class Movie(models.Model):
    """Kino"""
    title = models.CharField("Adı", max_length=100)
    country = models.CharField("Ölkə", max_length=30)
    runtime = models.CharField("Müddəti", max_length=30)
    description = models.TextField("Haqqında", blank=True)
    image = models.ImageField("Afişa", upload_to="movie_posters/")
    premiere = models.DateField("Premyera", default=date.today)
    timestamp = models.DateTimeField(auto_now_add=True)
    genres = models.ManyToManyField(Genre, verbose_name="Janr")
    tagline = models.CharField("Sloqan", max_length=100, default='')
    trailer = models.URLField("Treyler", max_length=2000, unique=True)
    year = models.PositiveSmallIntegerField("Buraxılış ili", default=2019)
    production = models.ManyToManyField(Production, verbose_name="İstehsalçı Şirkət")
    streaming = models.ManyToManyField(StreamingService, verbose_name="Yayım Platforması")
    certificate = models.ForeignKey(
        Certificate, verbose_name="Yaş Həddi", on_delete=models.SET_NULL, null=True
    )
    imdb = models.ForeignKey(
        ImdbRating, verbose_name="IMDb Reytinqi", on_delete=models.SET_NULL, null=True
    )
    directors = models.ManyToManyField(
        Director, verbose_name="Rejissor", related_name="film_director"
    )
    budget = models.PositiveIntegerField(
        "Büdcə", default=0, help_text="Məbləği dollarla göstərin"
    )
    box_office = models.BigIntegerField(
        "Ümumi gəlir", default=0, help_text="Məbləği dollarla göstərin"
    )
    # timestamp = models.DateTimeField(auto_now_add=True)
    movie_slug = models.SlugField(max_length=130, unique=True, null=True, blank=True)
    draft = models.BooleanField("Qaralama", default=False)

    def __str__(self):
        return self.title

    # def get_absolute_url(self):
    #    return reverse("movie_detail", kwargs={"slug": self.url})

    class Meta:
        verbose_name = "Kino"
        verbose_name_plural = "Kinolar"


class MovieShots(models.Model):
    """Kinodan şəkillər"""
    title = models.CharField("Başlıq", max_length=100)
    image = models.ImageField("Şəkil", upload_to="movie_shots/")
    movie = models.ForeignKey(Movie, verbose_name="Kino", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = "Kinodan şəkil"
        verbose_name_plural = "Kinodan şəkillər"


class RatingStar(models.Model):
    """Reytinq ulduzu"""
    value = models.SmallIntegerField("Dəyər", default=0)

    def __str__(self):
        return f'{self.value}'

    class Meta:
        verbose_name = "Reytinq ulduzu"
        verbose_name_plural = "Reytinq ulduzları"
        ordering = ["-value"]


class Rating(models.Model):
    """Reytinqlər"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    star = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name="Ulduz")
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, verbose_name="Kino", related_name="ratings"
    )

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = "Reytinq"
        verbose_name_plural = "Reytinqlər"


class Review(models.Model):
    """Rəylər"""
    spoiler = models.BooleanField(default=False)
    content = models.TextField("Mətn", max_length=800)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    likes = models.ManyToManyField(User, related_name='review_user_like', blank=True)
    unlikes = models.ManyToManyField(User, related_name='review_user_unlike', blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True, related_name="children"
    )
    movie = models.ForeignKey(
        Movie, verbose_name="Kino", on_delete=models.CASCADE, related_name="reviews"
    )

    def __str__(self):
        return f"{self.id} - {self.user.username}"

    @property
    def is_reply(self):
        return self.parent is not None

    class Meta:
        verbose_name = "Rəy"
        verbose_name_plural = "Rəylər"
        ordering = ["-timestamp"]
