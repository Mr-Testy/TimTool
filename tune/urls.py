"""timtool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from tune.views import (
    ListeTunes,
    ListeTunesFavoris,
    tunes_favoris_dashboard,
    generateur,
    generateur_group,
    comparateur,
    tune_lire,
    tune_lire_version,
    tune_favori_lire,
    tune_favori_add_sound,
    createABCTune,
    # DeleteTune,
    switch_favori,
    switch_status,
    delete_tune_favori,
    delete_sound
)

urlpatterns = [
    url(r'^liste/$', ListeTunes.as_view(), name="tune_liste",),
    url(r'^liste_favoris/$', ListeTunesFavoris.as_view(), name="tune_liste_favoris",),
    url(r'^liste_favoris/dashboard/$', tunes_favoris_dashboard, name="tunes_favoris_dashboard",),
    url(r'^generateur/$', generateur, name="generateur",),
    url(r'^generateur/(?P<slug>[\w-]*)$', generateur_group, name="generateur_group",),
    url(r'^comparateur/$', comparateur, name="comparateur",),
    url(r'^lire/(?P<slug>[\w-]+)$', tune_lire, name="tune_lire",),
    url(r'^lire/(?P<slug>[\w-]+)/(?P<version>[\w-]+)$', tune_lire_version, name="tune_lire_version",),
    url(r'^lire_favori/(?P<slug>[\w-]+)$', tune_favori_lire, name="tune_favori_lire",),
    url(r'^lire_favori/(?P<slug>[\w-]+)/add_sound/$', tune_favori_add_sound, name="tune_favori_add_sound",),
    url(r'^new_from_abc/$', createABCTune, name="tune_new_from_abc"),
    # url(r'^delete/(?P<slug>[\w-]+)/$', DeleteTune.as_view(), name='tune_delete'),
    url(r'^switch_favori/$', switch_favori, name='switch_favori'),
    url(r'^switch_status/$', switch_status, name='switch_status'),
    url(r'^tune_favori/delete/$', delete_tune_favori, name='delete_tune_favori'),
    url(r'^sound/delete/$', delete_sound, name='delete_sound'),
]
