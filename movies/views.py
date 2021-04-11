from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import viewsets, permissions, generics, renderers
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from datetime import datetime, date, timedelta
from django.utils import timezone
from drf_yasg import openapi
from django.conf import settings

from profiles.models import Watchlist, WatchlistTime  
from .models import Movie, Review, Director, Genre, StreamingService
from .service import (
    MovieFilter, PaginationMovies, get_movie_rating_star,
    get_review_action, get_movies_in_the_last_two_month,
    get_movies_catalog_queryset, WatchlistMovieFilter
)
from .serializers import (
    HomePageVideoSerializer, GenreListSerializer, MovieListSerializer, 
    StreamingListSerializer, MovieDetailSerializer, ReviewListSerializer,
    ReviewCreateSerializer, ReviewActionSerializer, ReviewSerializer, 
    ReviewDeleteSerializer, CreateRatingSerializer, UserWatchlistSerializer, 
    RemoveWatchlistSerializer, DirectorListSerializer, DirectorDetailSerializer, 
)

CATALOG_SECTION_NAMES = settings.CATALOG_SECTION_NAMES


class HomePageVideoView(APIView):
    """Ana səhifədəki video"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        obj = get_movies_in_the_last_two_month(self).first()
        serializer = HomePageVideoSerializer(obj)
        return Response(serializer.data, status=200)


class AllGenresListView(generics.ListAPIView):
    """Janrların siyahısını göstərmək"""

    queryset = Genre.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = GenreListSerializer


class NewMoviesListView(APIView):
    """Yeni kinoların siyahısını göstərmək"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    count_param = openapi.Parameter(
        'count', openapi.IN_QUERY, description="movies count", 
        type=openapi.TYPE_INTEGER, required=True
    )
    @swagger_auto_schema(
        manual_parameters=[count_param],
        responses={200: MovieListSerializer}
    )
    def get(self, request):
        end = request.GET.get('count', '')
        if end == '':
            return Response(
                {"count": "This field is required"}, status=400
            )
        try:
            end = int(end)
        except ValueError:
            return Response(
                {"count": "This field has to be number"}, status=400
            )
        end = 8 if end != 8 and end != 6 else end
        qs = get_movies_in_the_last_two_month(self)[1 : end + 1]
        serializer = MovieListSerializer(qs, many=True)
        return Response(serializer.data, status=200)


class MovieCatalogListView(APIView): 
    """Kinoları kataloqa görə göstərmək"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    count_param = openapi.Parameter(
        'count', openapi.IN_QUERY, description="movies count", 
        type=openapi.TYPE_INTEGER, required=True
    )
    section_param = openapi.Parameter(
        'section', openapi.IN_QUERY, 
        description="sections: {}".format(CATALOG_SECTION_NAMES), 
        type=openapi.TYPE_STRING, required=True
    )
    @swagger_auto_schema(
        manual_parameters=[count_param, section_param],
        responses={200: MovieListSerializer}
    )
    def get(self, request):
        return get_movies_catalog_queryset(self.request)


class PlatformsListView(generics.ListAPIView):
    """Platformalarin siyahisi"""

    queryset = StreamingService.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = StreamingListSerializer


class AllMoviesListView(generics.ListAPIView):
    """Bütün kinoların siyahısını göstərmək"""

    queryset = Movie.objects.filter(draft=False)
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = MovieListSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = MovieFilter
    pagination_class = PaginationMovies
    ordering_fields = ["imdb", "year"]
    search_fields = ["title"]
    ordering = ["-premiere", "-imdb"]


class SearchMovieListView(APIView):
    """Butun kinolarin arasinda limitle axtaris"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    title_param = openapi.Parameter(
        'title', openapi.IN_QUERY,
        type=openapi.TYPE_STRING, required=True
    )
    @swagger_auto_schema(
        manual_parameters=[title_param],
        responses={200: MovieListSerializer}
    )
    def get(self, request, *args, **kwargs):
        title = request.GET.get('title', '')
        if title != '':
            qs = Movie.objects.filter(
                draft=False, title__icontains=title
            ).order_by('imdb__vote')[:5]
            serializer = MovieListSerializer(qs, many=True)
            return Response(serializer.data, status=200)
        else:
            return Response(
                {"message": "For searching you need write something"}, 
                status=400
            )


class MovieDetailView(generics.RetrieveAPIView):
    """Tək bir kinonun məlumatlarını göstərmək"""

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = MovieDetailSerializer
    # lookup_field = 'movie_slug'

    def get_queryset(self):
        return get_movie_rating_star(self.request)


class ReviewListView(generics.RetrieveAPIView):
    """Bir kinoya aid rəyləri göstərmək"""

    queryset = Movie.objects.filter(draft=False)
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ReviewListSerializer


class ReviewCreateView(generics.CreateAPIView):
    """Rəylərin kinoya əlavə olunması"""

    permission_classes = [IsAuthenticated]
    serializer_class = ReviewCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewActionView(APIView):
    """Rəylərin like, unlike, reply olunması"""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ReviewActionSerializer, 
        responses={200: ReviewSerializer}
    )  
    def post(self, request):
        return get_review_action(self.request)
    

class ReviewDeleteView(generics.DestroyAPIView):
    """Rəylərin silinmesi"""

    permission_classes = [IsAuthenticated]
    serializer_class = ReviewDeleteSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        
        queryset = Review.objects.filter(user=self.request.user)
        return queryset

    def perform_destroy(self, instance):
        instance.delete()


class AddStarRatingView(generics.CreateAPIView):
    """Kinolara reytinqin əlavə olunması"""

    permission_classes = [IsAuthenticated]
    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddOrRemoveMovieWatchlistView(APIView):
    """Kinonu watchlist siyahisina elave etmek"""

    permission_classes = [IsAuthenticated]

    def post(self, request, movie_id):
        movie_obj = get_object_or_404(Movie, pk=movie_id)
        user_list, created = Watchlist.objects.get_or_create(user=request.user)
        if Watchlist.objects.filter(user=request.user, movie=movie_id).exists():
            user_list.movie.remove(movie_obj)
            return Response(
                {"message": "{} removed from your watchlist".format(movie_obj.title)}, 
                status=200
            )
        else:
            user_list.movie.add(movie_obj)
            return Response(
                {"message": "{} added to your watchlist".format(movie_obj.title)}, 
                status=200
            )


class RemoveMovieWatchlistView(APIView):
    """Kinolari watchlist siyahisindan cixartmaq"""

    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=RemoveWatchlistSerializer, 
        responses={200: "Successfully deleted movies titles"}
    )   
    def delete(self, request, *args, **kwargs):
        serializer = RemoveWatchlistSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            ids = serializer.validated_data.get('ids')
            w_obj = Watchlist.objects.filter(user=request.user).first()
            movies = WatchlistTime.objects.filter(
                watchlist=w_obj, movie__id__in=ids
            )
            if movies.exists() and movies.count() == len(ids):
                movies.delete()
                titles = [Movie.objects.get(id=obj).title for obj in ids]
                return Response({"movies": titles}, status=200)
            else:
                return Response(
                    {"message": "These movies not found in your watchlist"}, 
                    status=404
                )


class UserWatchlistView(generics.ListAPIView):
    """Userin watchlist siyahisi"""

    permission_classes = [IsAuthenticated]
    serializer_class = UserWatchlistSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = WatchlistMovieFilter
    pagination_class = PaginationMovies
    ordering_fields = ["movie__year",]
    search_fields = ["movie__title"]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WatchlistTime.objects.none()

        obj = Watchlist.objects.filter(user=self.request.user).first()
        return WatchlistTime.objects.filter(watchlist=obj)


class SearchMovieWatchlistView(APIView):
    """Userin watchlist siyahisinda limitle axtaris"""

    permission_classes = [IsAuthenticated]

    title_param = openapi.Parameter(
        'title', openapi.IN_QUERY,
        type=openapi.TYPE_STRING, required=True
    )
    @swagger_auto_schema(
        manual_parameters=[title_param],
        responses={200: MovieListSerializer}
    )
    def get(self, request, *args, **kwargs):
        title = request.GET.get('title', '')
        if title != '':
            qs = Movie.objects.filter(
                draft=False, title__icontains=title, 
                watchlist__user=request.user
            ).order_by('imdb__vote')[:5]
            serializer = MovieListSerializer(qs, many=True)
            return Response(serializer.data, status=200)
        else:
            return Response(
                {"message": "For searching you need write something"}, 
                status=400
            )


class DirectorListView(generics.ListAPIView):
    """Bütün rejissorların siyahısı"""

    queryset = Director.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = DirectorListSerializer
    pagination_class = PaginationMovies


class DirectorDetailView(generics.RetrieveAPIView):
    """Tek bir rejissorun melumatları"""

    queryset = Director.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = DirectorDetailSerializer


"""























# , id=self.kwargs['pk'])

# ReadOnlyModelViewSet
class DirectorReadOnly(viewsets.ReadOnlyModelViewSet):
    queryset = Director.objects.all()
    # serializer_class = DirectorListSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return DirectorListSerializer
        elif self.action == 'retrieve':
            return DirectorDetailSerializer


# ModelViewSet
class DirectorModel(viewsets.ModelViewSet):
    queryset = Director.objects.all()
    serializer_class = DirectorListSerializer

# ViewSet
class DirectorViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Director.objects.all()
        serializer = DirectorListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = Director.objects.all()
        director = get_object_or_404(queryset, pk=pk)
        serializer = DirectorDetailSerializer(director)
        return Response(serializer.data)


@ api_view(['POST'])
@ permission_classes([IsAuthenticated])
def review_action_view(request, *args, **kwargs):

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
"""
