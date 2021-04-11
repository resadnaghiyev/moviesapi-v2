from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.conf import settings
from .models import Movie


def user_did_save(sender, instance, created, *args, **kwargs):
    if created:
        obj = Movie.objects.get(title=instance.title)
        title = obj.title.lower().strip()
        slug = title.replace(" ", "-")
        x = "əöüıçşğ"
        y = "eouicsg" 
        mytable = slug.maketrans(x, y)
        obj.movie_slug = slug.translate(mytable)
        obj.save()

post_save.connect(user_did_save, sender=Movie)
