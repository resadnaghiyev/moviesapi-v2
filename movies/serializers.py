from django.conf import settings
from rest_framework import serializers
from profiles.serializers import ProfileSerializer
from profiles.models import Watchlist, WatchlistTime
from .models import (
    Director, Movie, Review, Rating, RatingStar, 
    Genre, ImdbRating, StreamingService
)

MAX_REVIEW_LENGTH = settings.MAX_REVIEW_LENGTH
REVIEW_ACTION_OPTIONS = settings.REVIEW_ACTION_OPTIONS
CATALOG_SECTION_NAMES = settings.CATALOG_SECTION_NAMES


class FilterReviewListSerializer(serializers.ListSerializer):
    """Parent reviews filter"""

    def to_representation(self, data):
        data = data.filter(parent=None).order_by('-timestamp')
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):
    """Children reviews"""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ReviewActionSerializer(serializers.Serializer):
    """Rəylərin like, unlike, reply olması"""

    review_id = serializers.IntegerField()
    action = serializers.CharField(help_text=f'actions: {REVIEW_ACTION_OPTIONS}')
    content = serializers.CharField(allow_blank=True, required=False)

    def validate_action(self, value):
        value = value.lower().strip()  # "Like " -> "like"
        if value not in REVIEW_ACTION_OPTIONS:
            raise serializers.ValidationError("This is not a valid action for review")
        return value


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Rəylərin əlavə olunması"""

    user = ProfileSerializer(source="user.profile", read_only=True)

    class Meta:
        model = Review
        fields = "__all__"

    def validate_content(self, value):
        if len(value) > MAX_REVIEW_LENGTH:
            raise serializers.ValidationError("This review is too long")
        return value


class ReviewDeleteSerializer(serializers.ModelSerializer):
    """Rəylərin silinməsi"""

    class Meta:
        model = Review
        fields = "__all__"


class ParentReviewSerializer(serializers.ModelSerializer):
    """Parent username"""

    # user = ProfileSerializer(source='user.profile', read_only=True)
    username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = ("username",)

    def get_username(self, obj):
        return obj.user.username


class ReviewSerializer(serializers.ModelSerializer):
    """Rəylərin gosterilmesi"""

    # user = ProfileSerializer(source='user.profile', read_only=True)
    likes = serializers.SerializerMethodField(read_only=True)
    unlikes = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    is_like = serializers.SerializerMethodField(read_only=True)
    is_unlike = serializers.SerializerMethodField(read_only=True)
    parent = ParentReviewSerializer(read_only=True)
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Review
        fields = (
            "id", "username", "content", "likes", "is_like", "unlikes",
            "is_unlike", "spoiler", "is_reply", "timestamp", "parent", "children",
        )

    def get_likes(self, obj):
        return obj.likes.count()

    def get_unlikes(self, obj):
        return obj.unlikes.count()

    def get_username(self, obj):
        return obj.user.username
    
    def get_is_like(self, obj):
        if self.context['request'].user in obj.likes.all():
            return True
        else:
            return False

    def get_is_unlike(self, obj):
        if self.context['request'].user in obj.unlikes.all():
            return True
        else:
            return False


class ReviewListSerializer(serializers.ModelSerializer):
    """Rəylərin list şəklində göstərilməsi"""

    review_count = serializers.SerializerMethodField(read_only=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        fields = ("review_count", "reviews")

    def get_review_count(self, obj):
        return obj.reviews.count()


class GenreListSerializer(serializers.ModelSerializer):
    """Janrları göstərmək"""

    class Meta:
        model = Genre
        fields = "__all__"  


class ImdbListSerializer(serializers.ModelSerializer):
    """IMDb reytinqini gostermek"""

    votes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ImdbRating
        fields = ("point", "votes")

    def get_votes(self, obj):
        votes = obj.votes
        return f"{votes:,}"


class DirectorListSerializer(serializers.ModelSerializer):
    """Rejissorlarin siyahisi"""

    class Meta:
        model = Director
        fields = ("id", "name")


class DirectorDetailSerializer(serializers.ModelSerializer):
    """Tek rejissorun melumatlari"""

    class Meta:
        model = Director
        fields = "__all__"


class MovieListSerializer(serializers.ModelSerializer):
    """Kinoların siyahısı"""

    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    imdb = serializers.SlugRelatedField(slug_field="point", read_only=True)

    class Meta:
        model = Movie
        fields = ("id", "title", "image", "genres", "imdb")

    # def get_user_star(self, instance):
    #    user_id = self.context['request'].user


class MovieDetailSerializer(serializers.ModelSerializer):
    """Kinonun detallari"""

    certificate = serializers.SlugRelatedField(slug_field="rated", read_only=True)
    imdb = ImdbListSerializer(read_only=True)
    rating_user = serializers.IntegerField(default=0)
    middle_star = serializers.DecimalField(max_digits=2, decimal_places=1)
    count_votes = serializers.SerializerMethodField(read_only=True)
    is_watchlist = serializers.BooleanField(default=False)
    genres = GenreListSerializer(read_only=True, many=True)
    directors = serializers.SlugRelatedField(
        slug_field="name", read_only=True, many=True
    )
    production = serializers.SlugRelatedField(
        slug_field="name", read_only=True, many=True
    )
    streaming = serializers.SlugRelatedField(
        slug_field="name", read_only=True, many=True
    )
    budget = serializers.SerializerMethodField(read_only=True)
    box_office = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Movie
        exclude = ("draft",)

    def get_budget(self, obj):
        return f"{obj.budget:,}"

    def get_box_office(self, obj):
        return f"{obj.box_office:,}"
    
    def get_count_votes(self, obj):
        return obj.ratings.count()


class HomePageVideoSerializer(serializers.ModelSerializer):
    """Ana səhifədəki video"""

    welcome_text = serializers.SerializerMethodField(read_only=True)
    video_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Movie
        fields = ("title", "video_id", "welcome_text")

    def get_video_id(self, obj):
        video_id = str(obj.trailer)
        start = video_id.find("=") + 1
        end = video_id.find("&") + 1
        if end < start:
            return video_id[start:]
        return video_id[start:end]

    def get_welcome_text(self, obj):
        return f"We are very happy to welcome you to the our movie site. \
                 We are doing some interesting works here and we are hopeful that \
                 you enjoys this site, popular and new movies, \
                 tv-series will be available for you!"


class StreamingListSerializer(serializers.ModelSerializer):
    """Janrları göstərmək"""

    class Meta:
        model = StreamingService
        fields = ("image", "slug")


class CreateRatingSerializer(serializers.ModelSerializer):
    """Kinolara reytinqin əlavə olunması"""

    # user = ProfileSerializer(source='user.profile', read_only=True)

    class Meta:
        model = Rating
        fields = ("star", "movie")

    def create(self, validated_data):
        rating, _ = Rating.objects.update_or_create(
            user=validated_data.get("user", None),
            movie=validated_data.get("movie", None),
            defaults={"star": validated_data.get("star")},
        )
        return rating


class UserWatchlistSerializer(serializers.ModelSerializer):
    # User Watchlist siyahisi

    movie = MovieListSerializer(read_only=True)

    class Meta:
        model = WatchlistTime
        fields = ("movie",)


class RemoveWatchlistSerializer(serializers.Serializer):
    """Rəylərin like, unlike, reply olması"""

    ids = serializers.CharField(
        required=True, help_text='Example -- "ids": "1,2,3"'
    )

    def validate_ids(self, value):
        value = value.split(",")
        try:
            value = set(map(int, value))
        except ValueError:
            raise serializers.ValidationError(
                "This field is required and has to be numbers"
            )
        return value
