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
    added_by = serializers.ReadOnlyField(source='added_by.username')

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Tune
        fields = ('name', 'key', 'type', 'slug', 'added_by', 'versions', 'titles', 'composers')
        read_only_fields = ('date_creation',)

    versions = serializers.IntegerField(
    source='abcs.count', 
    read_only=True
    )
    titles = TitleSeriallizer(many=True, read_only=True)
    composers = ComposerSeriallizer(many=True, read_only=True)

class TuneTypeSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Tune
        fields = ('type',)

class TuneFavoriSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = TuneFavori
        fields = ('personal_note', 'date_creation', 'status', 'of_tune')
        read_only_fields = ('date_creation',)
        ordering = ["-date_creation"]

    of_tune = TuneSerializer(read_only=True)