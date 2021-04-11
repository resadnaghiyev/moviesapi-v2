from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Avg, Sum, Q, Count
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.conf import settings

from profiles.models import WatchlistTime
from .models import Movie, Review
from .serializers import (
    ReviewActionSerializer, ReviewSerializer, MovieListSerializer
)

CATALOG_SECTION_NAMES = settings.CATALOG_SECTION_NAMES


def get_movie_rating_star(request):
    if request.user.is_authenticated:
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=Avg(
                'ratings__star', filter=Q(ratings__user=request.user)
            )
        ).annotate(
            is_watchlist=Count(
                'watchlist__user', filter=Q(watchlist__user=request.user)
            )
        ).annotate(
            middle_star=Avg('ratings__star')
        ).order_by('id')
        return movies
    else:
        movies = Movie.objects.filter(draft=False).annotate(
            middle_star=Avg('ratings__star')
        ).order_by('id')
        return movies


def get_movies_in_the_last_two_month(self):
    last_two_month = date.today() - timedelta(days=2920)
    qs = Movie.objects.filter(draft=False, premiere__gte=last_two_month)
    qs = qs.filter(imdb__point__gte=6.0).order_by('-imdb__votes')
    return qs


def get_movies_catalog_queryset(request):
    movies_count = request.GET.get('count', '')
    section_name = request.GET.get('section', '')

    if movies_count == '' or section_name == '':
        return Response(
            {
                "count": "This field is required",
                "section": "This field is required"
            }, status=400
        )
    try:
        movies_count = int(movies_count)
        movies_count = 12 if movies_count != 12 and movies_count != 6 else movies_count
    except ValueError:
        return Response(
            {"count": "This field has to be a number"}, status=400
        )

    section_name = section_name.lower().strip()
    if section_name not in CATALOG_SECTION_NAMES:
        return Response(
            {"section": "This is not a valid section name for catalog"}, status=400
        )

    if section_name == "new-added":
        last_days = timezone.now() - timedelta(days=100)
        queryset = Movie.objects.filter(
            draft=False, timestamp__gte=last_days, premiere__lt=last_days
        ).order_by('-timestamp')[:movies_count]
        serializer = MovieListSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    elif section_name == "most-popular":
        queryset = Movie.objects.filter(
            draft=False, imdb__point__range=[7.0, 8.0], imdb__votes__gte=300000
        ).order_by('-premiere')[:movies_count]
        serializer = MovieListSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    elif section_name == "most-rated":
        queryset = Movie.objects.filter(
            draft=False, imdb__votes__gte=800000
        ).order_by('-imdb__point')[:movies_count]
        serializer = MovieListSerializer(queryset, many=True)
        return Response(serializer.data, status=200)


def get_review_action(request):
    serializer = ReviewActionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        review_id = data.get("review_id")
        action = data.get("action")
        content = data.get("content")
        qs = Review.objects.filter(id=review_id)
        if not qs.exists():
            return Response({}, status=404)
        obj = qs.first()

        if action == "like":
            if request.user in obj.likes.all():
                obj.likes.remove(request.user)
            else:
                obj.likes.add(request.user)
                obj.unlikes.remove(request.user)
            serializer = ReviewSerializer(obj)
            return Response(serializer.data, status=200)

        elif action == "unlike":
            if request.user in obj.unlikes.all():
                obj.unlikes.remove(request.user)
            else:
                obj.unlikes.add(request.user)
                obj.likes.remove(request.user)
            serializer = ReviewSerializer(obj)
            return Response(serializer.data, status=200)

        elif action == "reply":
            if content == "":
                return Response({"message": "You cannot post empty review"}, status=401)
            else:
                new_review = Review.objects.create(
                    user=request.user,
                    parent=obj,
                    content=content,
                    movie=obj.movie,
                )
                serializer = ReviewSerializer(new_review)
                return Response(serializer.data, status=201)
    return Response({}, status=200)


class PaginationMovies(PageNumberPagination):
    page_size = 10
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):

    def filter(self, qs, value):
        return super().filter(qs.distinct(), value)


class MovieFilter(filters.FilterSet):
    genres = CharFilterInFilter(field_name='genres__url', lookup_expr='in')
    rate = CharFilterInFilter(field_name='certificate__url', lookup_expr='in')
    platforms = CharFilterInFilter(field_name='streaming__slug', lookup_expr='in')
    imdb = filters.RangeFilter(field_name='imdb__point', lookup_expr='in')
    year = filters.RangeFilter()

    class Meta:
        model = Movie
        fields = ['genres', 'rate', 'platforms', 'imdb', 'year']

    # ?year_min=2010&year_max=2020&genres=sci_fi,action
    # ?imdb_min=8.2&imdb_max=8.9&rate=16_plus


class WatchlistMovieFilter(filters.FilterSet):
    genres = CharFilterInFilter(field_name='movie__genres__url', lookup_expr='in')
    rate = CharFilterInFilter(field_name='movie__certificate__url', lookup_expr='in')
    platforms = CharFilterInFilter(field_name='movie__streaming__slug', lookup_expr='in')
    imdb = filters.RangeFilter(field_name='movie__imdb__point', lookup_expr='in')
    year = filters.RangeFilter(field_name='movie__year', lookup_expr='in')

    class Meta:
        model = WatchlistTime
        fields = ['genres', 'rate', 'platforms', 'imdb', 'year']  # , 'production']



# class DynamicSearchFilter(filters.SearchFilter):
#     def get_search_fields(self, view, request):
#         return request.GET.getlist('search_fields', [])
