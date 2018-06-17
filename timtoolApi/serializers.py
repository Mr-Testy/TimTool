from rest_framework import serializers
from tune.models import Tune, Title, Composer, TuneFavori

class TitleSeriallizer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ('name',)

class ComposerSeriallizer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ('name',)

class TuneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tune
        fields = ('name', 'key', 'type', 'slug')

class TuneTypeSerializer(serializers.ModelSerializer):

    class Meta:
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