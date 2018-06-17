from rest_framework import serializers
from tune.models import Tune, Title, Composer, TuneFavori

class TitleSeriallizer(serializers.ModelSerializer):
    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Title
        fields = ('name',)

class ComposerSeriallizer(serializers.ModelSerializer):
    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Title
        fields = ('name',)

class TuneSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    titles = TitleSeriallizer(many=True, read_only=True)

    @staticmethod
    def setup_eager_loading(queryset):
        # prefetch_related for "to-many" relationships
        queryset = queryset.prefetch_related(
            'titles')
        return queryset

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Tune
        fields = ('name', 'key', 'type', 'slug', 'added_by', 'titles')
        read_only_fields = ('date_creation',)

class TuneTypeSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Tune
        fields = ('type',)

class TuneFavoriSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    of_tune = TuneSerializer(read_only=True)

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related(
            'of_tune')

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = TuneFavori
        fields = ('personal_note', 'date_creation', 'status', 'of_tune')
        read_only_fields = ('date_creation',)
        ordering = ["-date_creation"]