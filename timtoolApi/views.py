from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TuneSerializer, TuneFavoriSerializer, TuneDetailsSerializer
from tune.models import Tune, TuneFavori_user
from user.models import User
from .permissions import IsOwner, AllowOptionsAuthentication
from django.http import HttpResponse, Http404, HttpResponseForbidden, JsonResponse
from django.core.cache import cache
import datetime

class TuneList(APIView):

    def get(self, request, format=None):
        limit = int(self.request.query_params.get('limit', 0))
        offset = int(self.request.query_params.get('offset', limit+50))
        if cache.get('tunes') == None:
            tunes = Tune.objects.all()
            tunes = TuneSerializer.setup_eager_loading(tunes)
            tunes = TuneSerializer(tunes, many=True).data
            cache.set('tunes', tunes, None)
        return Response(cache.get('tunes')[limit :offset])

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
        if cache.get('tune='+slug) == None:
            tune = self.get_object(slug)
            tune = TuneDetailsSerializer(tune).data
            cache.set('tune='+slug, tune, None)
        return Response(cache.get('tune='+slug))

class TuneFavoriList(APIView):
    permission_classes = (AllowOptionsAuthentication,)

    def get(self, request, format=None):
        if cache.get('tunes_favoris='+self.request.user.username) == None:
            tunes_favoris = TuneFavori_user.objects.filter(of_user=self.request.user)
            tunes_favoris = TuneFavoriSerializer.setup_eager_loading(tunes_favoris)
            tunes_favoris = TuneFavoriSerializer(tunes_favoris, many=True).data
            cache.set('tunes_favoris='+self.request.user.username, tunes_favoris, None)
        return Response(cache.get('tunes_favoris='+self.request.user.username))

class SwitchFavori(APIView):
    permission_classes = (AllowOptionsAuthentication,)

    def post(self, request):
        tune_slug = request.data["tune_slug"]

        if tune_slug:
            try:
                tune_favori = TuneFavori_user.objects.get(of_user=request.user, of_tune__slug=tune_slug)
            except TuneFavori_user.DoesNotExist: 
                tune_favori = None

            if tune_favori:
                tune_favori.delete()
                return JsonResponse({"result": "deleted"})
            else:
                tune = Tune.objects.get(slug=tune_slug)
                create_tune_favori = TuneFavori_user(of_user=request.user, of_tune=tune)
                create_tune_favori.save()
                user = User.objects.get(id=request.user.id)
                user.tunes_favoris.add(create_tune_favori)
                return JsonResponse({"result": "added"})
        return JsonResponse({"result": "unchanged"})