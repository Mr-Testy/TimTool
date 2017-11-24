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

from user.views import (contact,
                        profile,
                        toggle_menu,
                        ListeGroups,
                        CreateGroup,
                        LireGroup,
                        updateGroup,
                        updateGroupRoles,
                        updateProfil,
                        joinGroup,
                        leaveGroup,
                        add_favoris_to_group,
                        groupe_switch_favori,
                        groupe_switch_role,
                        ListeUserGroups
                        )

urlpatterns = [
    url(r'^contact/$', contact, name="contact"),
    url(r'^profile/$', profile, name='profile'),
    url(r'^profile/update/$', updateProfil, name='profile_update'),
    url(r'^toggle_menu/$', toggle_menu, name='toggle_menu'),
    url(r'^groupe/liste/$', ListeGroups.as_view(), name="groupe_liste",),
    url(r'^groupe/new/$', CreateGroup.as_view(), name="groupe_new"),
    url(r'^groupe/lire/(?P<slug>[\w-]+)/$', LireGroup.as_view(), name="groupe_lire"),
    url(r'^groupe/update/(?P<slug>[\w-]+)/$', updateGroup, name="groupe_update"),
    url(r'^groupe/update_roles/(?P<slug>[\w-]+)/$', updateGroupRoles, name="groupe_update_roles"),
    url(r'^groupe/join/$', joinGroup, name="groupe_join"),
    url(r'^groupe/leave/$', leaveGroup, name="groupe_leave"),
    url(r'^groupe/add_favoris/(?P<slug>[\w-]+)/$', add_favoris_to_group, name="groupe_add_favoris"),
    url(r'^groupe/switch_favori/$', groupe_switch_favori, name='groupe_switch_favori'),
    url(r'^groupe/switch_role/$', groupe_switch_role, name='groupe_switch_role'),
    url(r'^groupe/mygroups/$', ListeUserGroups.as_view(), name='user_groupe_liste'),
]
