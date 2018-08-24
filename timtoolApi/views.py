from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TuneSerializer, TuneTypeSerializer, TuneFavoriSerializer
from tune.models import Tune, TuneFavori_user
from .permissions import IsOwner
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.core.cache import cache
import datetime

class TuneTypeList(APIView):

    def get(self, request, format=None):
        queryset = Tune.objects.order_by("type").distinct("type")
        types = [o.type for o in queryset]
        return Response(types)

class TuneKeyList(APIView):

    def get(self, request, format=None):
        queryset = Tune.objects.order_by("key").distinct("key")
        keys = [o.key for o in queryset]
        return Response(keys)

class TuneList(APIView):

    def get(self, request, format=None):
        if cache.get('tunes') == None:
            limit = int(self.request.query_params.get('limit', 0))
            offset = int(self.request.query_params.get('offset', limit+50))
            tunes = Tune.objects.all()
            tunes = TuneSerializer.setup_eager_loading(tunes)
            tunes =  TuneSerializer(tunes, many=True).data
            cache.set('tunes', tunes, None)
        return Response(cache.get('tunes'))

class TuneDetails(APIView):
    """
    Retrieve 
    """
    def get_object(self, slug):
        try:
            return Tune.objects.get(slug=slug)
        except Tune.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        tune = self.get_object(slug)
        serializer = TuneSerializer(tune)
        return Response(serializer.data)

class TuneFavoriList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        queryset = TuneFavori_user.objects.filter(of_user=self.request.user)
        pre_qs = TuneFavoriSerializer.setup_eager_loading(queryset)
        serializer = TuneFavoriSerializer(pre_qs, many=True)
        return Response(serializer.data)