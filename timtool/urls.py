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
from django.contrib import admin
from django.conf.urls import url, include
from django.views.i18n import JavaScriptCatalog

from tune.views import home, about

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^timtoolApi/', include('timtoolApi.urls')),
    url(r'^$', home, name="accueil"),
    url(r'^(?P<lang>[\w-]*)$', home, name="accueil_lang"),
    url(r'^about/$', about, name="about"),
    url(r'^tune/', include('tune.urls', namespace='tune')),
    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^account/', include('allauth.urls')),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
