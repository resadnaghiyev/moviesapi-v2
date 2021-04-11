from django.apps import AppConfig


class MoviesConfig(AppConfig):
    name = 'movies'
    verbose_name = "Kino"

    def ready(self):
        import movies.signals
