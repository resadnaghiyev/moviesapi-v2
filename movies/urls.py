from django.urls import path, re_path
# from rest_framework.routers import DefaultRouter
# from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
    # home page urls
    path("home-page-video/", views.HomePageVideoView.as_view()),
    path("genres/", views.AllGenresListView.as_view()),
    path("new-movies/", views.NewMoviesListView.as_view()),
    path("catalog-movies/", views.MovieCatalogListView.as_view()),
    path("platforms/", views.PlatformsListView.as_view()),
    # all movies and detail urls
    path("movies/", views.AllMoviesListView.as_view()),
    path("movie/<int:pk>/", views.MovieDetailView.as_view()),
    # review urls
    path("review/create/", views.ReviewCreateView.as_view()),
    path("review/action/", views.ReviewActionView.as_view()),
    path("movie/<int:pk>/reviews/", views.ReviewListView.as_view()),
    path("review/<int:pk>/delete/", views.ReviewDeleteView.as_view()),
    # all directors and detail urls
    path("directors/", views.DirectorListView.as_view()),
    path("director/<int:pk>/", views.DirectorDetailView.as_view()),
    # profile urls
    path("add-rating/", views.AddStarRatingView.as_view()),
    path("add-watchlist/<int:movie_id>/", views.AddOrRemoveMovieWatchlistView.as_view()),
    path("user-watchlist/", views.UserWatchlistView.as_view()),
    path("remove-watchlist/", views.RemoveMovieWatchlistView.as_view()),
    # search
    path("search-movie/", views.SearchMovieListView.as_view()),
    path("search-watchlist/", views.SearchMovieWatchlistView.as_view())
]



# re_path(r'^index/$', views.index, name='index'),
# re_path(r'^bio/(?P<username>\w+)/$', views.bio, name='bio'),
# re_path(r'^weblog/', include('blog.urls')),

# re_path(r'^new/$', views.NewMoviesListView.as_view()),


# router = DefaultRouter()

# # router.register(r'director-read', views.DirectorReadOnly, basename='director')
# router.register(r'movies', views.AllMoviesListView, basename='movies')

# urlpatterns = router.urls

# director_list = views.DirectorModel.as_view({
#     'get': 'list',
#     'post': 'create'
# })
# director_detail = views.DirectorModel.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })

# urlpatterns = format_suffix_patterns([
#     path('director/', director_list, name='director-list'),
#     path('director/<int:pk>/', director_detail, name='director-detail'),
# ])
