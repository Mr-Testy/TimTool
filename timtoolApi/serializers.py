from rest_framework import serializers
from tune.models import Tune, Title, Composer, TuneFavori, ABCTune

class ABCTuneSeriallizer(serializers.ModelSerializer):
    class Meta:
        model = ABCTune
        exclude = ('tune',)

class TitleSeriallizer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ('name',)

class ComposerSeriallizer(serializers.ModelSerializer):
    class Meta:
        model = Composer
        fields = ('name',)

class TuneSerializer(serializers.ModelSerializer):
    titles = TitleSeriallizer(many=True)

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related(
            'titles')
        return queryset

    class Meta:
        model = Tune
        fields = ('name', 'key', 'type', 'slug', 'date_creation', 'titles')

class TuneDetailsSerializer(serializers.ModelSerializer):
    titles = TitleSeriallizer(many=True)
    composers = ComposerSeriallizer(many=True)
    abcs = ABCTuneSeriallizer(many=True)

    class Meta:
        model = Tune
        fields = ('name', 'key', 'type', 'slug', 'description', 'date_creation', 'titles', 'composers', 'abcs')

class TuneFavoriSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    of_tune = TuneSerializer()

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related(
            'of_tune')
        return queryset

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = TuneFavori
        fields = ('personal_note', 'date_creation', 'status', 'of_tune')
        read_only_fields = ('date_creation',)
        ordering = ["-date_creation"]