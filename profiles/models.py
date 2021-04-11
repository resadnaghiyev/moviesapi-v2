from django.db import models
from django.conf import settings
from movies.models import Movie

User = settings.AUTH_USER_MODEL


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # image =
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class WatchlistTime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watchlist = models.ForeignKey("Watchlist", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movie.title}"

    class Meta:
        ordering = ['-timestamp']


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ManyToManyField(
        Movie, blank=True, related_name='watchlist', through=WatchlistTime
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Watchlist user of - {self.user.username}"
