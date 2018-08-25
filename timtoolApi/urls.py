from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import TuneList, TuneDetails, TuneFavoriList
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = {
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^tunes/types/$', TuneTypeList.as_view(), name="types"),
    # url(r'^tunes/keys/$', TuneKeyList.as_view(), name="keys"),
    url(r'^tunes/$', TuneList.as_view(), name="tune_list"),
    url(r'^favoris/$', TuneFavoriList.as_view(), name="tune_favori_list"),
	url(r'^tune/(?P<slug>[\w-]+)/$', TuneDetails.as_view(), name="tune_details",),
    url(r'^get-token/', obtain_auth_token),
}

urlpatterns = format_suffix_patterns(urlpatterns)