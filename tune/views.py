from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from pathlib import Path
import random

from .models import Tune, TuneFavori, TuneFavori_group, TuneFavori_user, Audio_clyp_user_favori, Audio_clyp_group_favori, Audio_clyp
from .forms import GenerateurForm, UploadABCFileForm, TextAreaABCForm, ClypForm
from user.models import User, GroupExtend
from user.forms import CompareUserForm
from tune.abc import handle_uploaded_file, handle_text_area, constructABC_from_tune, constructSVG_from_ABC, constructMIDI_from_ABC


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


def home(request, lang=None):
    tunes = Tune.objects.all()[:10]
    groups = GroupExtend.objects.all()[:10]
    users = User.objects.all()[:10]
    clyps = Audio_clyp.objects.all()[:5]
    return render(request, 'tune/accueil.html', {"tunes": tunes, "groups": groups, "users": users, "clyps": clyps})


def about(request):
    return render(request, 'tune/about.html')


class ListeTunes(ListView):
    model = Tune
    context_object_name = "all_tunes"
    template_name = "tune/tune_liste.html"
    paginate_by = 100

    def get_queryset(self):
        q_name = self.request.GET.get("q_name", None)
        q_type = self.request.GET.get("q_type", None)
        q_key = self.request.GET.get("q_key", None)
        tunes = Tune.objects.all()
        if q_name:
            tunes = tunes.filter(name__icontains=q_name)
        if q_type:
            tunes = tunes.filter(type=q_type)
        if q_key:
            tunes = tunes.filter(key=q_key)
        if q_name or q_type or q_key:
            messages.success(self.request, _('The following filters have been applied : "name" contains "%(name)s" | "type" = "%(type)s" | "key" = "%(key)s"') % {
                'name': q_name,
                'type': q_type,
                'key': q_key
            })
        return tunes


class ListeTunesFavoris(ListView):
    model = TuneFavori_user
    context_object_name = "all_tunes_favoris"
    template_name = "tune/tune_liste_favoris.html"
    paginate_by = 200

    def get_queryset(self):
        q_name = self.request.GET.get("q_name", None)
        q_type = self.request.GET.get("q_type", None)
        q_key = self.request.GET.get("q_key", None)
        q_status = self.request.GET.get("q_status", None)
        tunes_favoris = TuneFavori_user.objects.filter(of_user=self.request.user)
        if q_name:
            tunes_favoris = tunes_favoris.filter(of_tune__name__icontains=q_name)
        if q_type:
            tunes_favoris = tunes_favoris.filter(of_tune__type=q_type)
        if q_key:
            tunes_favoris = tunes_favoris.filter(of_tune__key=q_key)
        if q_status == "Learned":
            tunes_favoris = tunes_favoris.filter(status=True)
        elif q_status == "Not learned":
            tunes_favoris = tunes_favoris.filter(status=False)
        if q_name or q_type or q_key or q_status == "Learned" or q_status == "Not learned":
            messages.success(self.request, _('The following filters have been applied : "name" contains "%(name)s" | "type" = "%(type)s" | "key" = "%(key)s" | "status" = "%(status)s"') % {
                'name': q_name,
                'type': q_type,
                'key': q_key,
                'status': q_status
            })
        return tunes_favoris


@login_required
def tunes_favoris_dashboard(request):
    tunes_favoris = request.user.tunes_favoris.all()
    tunes = Tune.objects.filter(tunefavori__in=tunes_favoris)
    types = list(tunes.order_by('type').values('type').distinct())
    dashboard = {}
    dashboard["all"] = [0, 0, 0]
    for type in types:
        type = type["type"]
        all = tunes_favoris.filter(of_tune__type=type).count()
        learned = tunes_favoris.filter(of_tune__type=type, status=True).count()
        not_learned = tunes_favoris.filter(of_tune__type=type, status=False).count()
        dashboard[type] = [all, learned, not_learned]
        dashboard["all"] = [dashboard["all"][0] + all, dashboard["all"][1] + learned, dashboard["all"][2] + not_learned]

    return render(request, "tune/dashboard.html", {"dashboard": dashboard
        })


@login_required
def generateur(request):
    sets = ""
    tunes = ""
    tunes_favoris = ""
    sets_favoris = ""
    final_tunes_sets = []
    final_favoris_sets = []
    if request.method == 'POST':
        # list_of = request.POST.get("list_of", None)
        form = GenerateurForm(request.POST)
        if form.is_valid():
            list_of = form.cleaned_data["list_of"]
            among = form.cleaned_data["among"]
            types = form.cleaned_data["types"]
            keys = form.cleaned_data["keys"]
            if among == "Tunes favoris appris":
                tunes_favoris = TuneFavori_user.objects.filter(
                    status=1,
                    of_user=request.user,
                    of_tune__type__in=types,
                    of_tune__key__in=keys,
                )
                if tunes_favoris.count() == 0:
                    messages.warning(request, _(
                        'The list of "%(list_of)s" among "%(among)s" is empty. Modify your search criterias.') % {
                    'list_of': list_of,
                    'among': among
                    })
            elif among == "Tunes Favoris non appris":
                tunes_favoris = TuneFavori_user.objects.filter(
                    status=0,
                    of_user=request.user,
                    of_tune__type__in=types,
                    of_tune__key__in=keys,
                )
                if tunes_favoris.count() == 0:
                    messages.warning(request, _(
                    'The list of "%(list_of)s" among "%(among)s" is empty. Modify your search criterias.') % {
                    'list_of': list_of,
                    'among': among
                    })
            elif among == "Tous les Tunes Favoris":
                tunes_favoris = TuneFavori_user.objects.filter(
                    of_user=request.user,
                    of_tune__type__in=types,
                    of_tune__key__in=keys,
                )
                if tunes_favoris.count() == 0:
                    messages.warning(request, _(
                        'The list of "%(list_of)s" among "%(among)s" is empty. Modify your search criterias.') % {
                    'list_of': list_of,
                    'among': among
                    })
            elif among == "Tous les Tunes du site":
                tunes = Tune.objects.filter(type__in=types,
                                            key__in=keys,)
                if tunes.count() == 0:
                    messages.warning(request, _(
                        'The list of "%(list_of)s" among "%(among)s" is empty. Modify your search criterias.') % {
                    'list_of': list_of,
                    'among': among
                    })
            tunes = list(tunes)
            random.shuffle(tunes)
            tunes_favoris = list(tunes_favoris)
            random.shuffle(tunes_favoris)
            if list_of == "Sets":
                if len(tunes_favoris) > 0:
                    sets_favoris = {}
                    types_init = {}
                    for type in types:
                        types_init[type] = 0
                        sets_favoris[type] = []
                    for tune in tunes_favoris:
                        if types_init[tune.of_tune.type] == 3:
                            types_init[tune.of_tune.type] = 0
                            sets_favoris[tune.of_tune.type].insert(0, tune.of_tune.type)
                            final_favoris_sets.append(sets_favoris[tune.of_tune.type])
                            sets_favoris[tune.of_tune.type] = []
                        sets_favoris[tune.of_tune.type].append(tune)
                        types_init[tune.of_tune.type] = types_init[tune.of_tune.type] + 1
                    for key, final_set in sets_favoris.items():
                        if len(final_set) > 0:
                                final_set.insert(0, key)
                                final_favoris_sets.append(final_set)

                if len(tunes) > 0:
                    sets = {}
                    types_init = {}
                    for type in types:
                        types_init[type] = 0
                        sets[type] = []
                    for tune in tunes:
                        if types_init[tune.type] == 3:
                            types_init[tune.type] = 0
                            sets[tune.type].insert(0, tune.type)
                            final_tunes_sets.append(sets[tune.type])
                            sets[tune.type] = []
                        sets[tune.type].append(tune)
                        types_init[tune.type] = types_init[tune.type] + 1
                    for key, final_set in sets.items():
                        if len(final_set) > 0:
                                final_set.insert(0, key)
                                final_tunes_sets.append(final_set)
            messages.success(
                request,
                _(
                'The list of "%(list_of)s" among "%(among)s" has been generated') % {
                'list_of': list_of,
                'among': among
                })
    else:
        form = GenerateurForm()
    return render(request, 'tune/generateur.html', {'form': form,
                                                    'tunes': tunes,
                                                    'sets': final_tunes_sets,
                                                    'tunes_favoris': tunes_favoris,
                                                    'sets_favoris': final_favoris_sets})


@login_required
def generateur_group(request, slug):
    sets = ""
    tunes = ""
    tunes_favoris = ""
    sets_favoris = ""
    final_tunes_sets = []
    final_favoris_sets = []
    try:
        group_to_generate = GroupExtend.objects.get(slug=slug)
    except GroupExtend.DoesNotExist:
        messages.error(request, _('The group "%(slug)s" doesn\'t exist') % {'slug': slug})
        return redirect("accueil")
    except GroupExtend.MultipleObjectsReturned:
        messages.error(request, _(
            'There are several groupes "%(slug)s". Impossible to generate tunes.') % {'slug': slug})
        return redirect("accueil")

    if request.method == 'POST':
        # list_of = request.POST.get("list_of", None)
        form = GenerateurForm(request.POST)
        if form.is_valid():
            list_of = form.cleaned_data["list_of"]
            among = form.cleaned_data["among"]
            types = form.cleaned_data["types"]
            keys = form.cleaned_data["keys"]
            if among == "Tunes favoris appris":
                tunes_favoris = TuneFavori_group.objects.filter(
                    status=1,
                    of_group=group_to_generate,
                    of_tune__type__in=types,
                    of_tune__key__in=keys,
                )
                if tunes_favoris.count() == 0:
                    messages.warning(request, _(
                    'The list of "%(list_of)s" among "%(among)s" is empty. Modify your search criterias.') % {
                    'list_of': list_of,
                    'among': among
                    })
            elif among == "Tunes Favoris non appris":
                tunes_favoris = TuneFavori_group.objects.filter(
                    status=0,
                    of_group=group_to_generate,
                    of_tune__type__in=types,
                    of_tune__key__in=keys,
                )
                if tunes_favoris.count() == 0:
                    messages.warning(request, _(
                        'The list of "%(list_of)s" among "%(among)s" is empty. Modify your search criterias.') % {
                    'list_of': list_of,
                    'among': among
                    })
            elif among == "Tous les Tunes Favoris":
                tunes_favoris = TuneFavori_group.objects.filter(
                    of_group=group_to_generate,
                    of_tune__type__in=types,
                    of_tune__key__in=keys
                )
                if tunes_favoris.count() == 0:
                    messages.warning(request, _(
                        'The list of "%(list_of)s" among "%(among)s" is empty. Modify your search criterias.') % {
                    'list_of': list_of,
                    'among': among
                    })
            elif among == "Tous les Tunes du site":
                tunes = Tune.objects.filter(type__in=types,
                                            key__in=keys,)
                if tunes.count() == 0:
                    messages.warning(request, _(
                        'The list of "%(list_of)s" among "%(among)s" is empty. Modify your search criterias.') % {
                    'list_of': list_of,
                    'among': among
                    })
            tunes = list(tunes)
            random.shuffle(tunes)
            tunes_favoris = list(tunes_favoris)
            random.shuffle(tunes_favoris)
            if list_of == "Sets":
                if len(tunes_favoris) > 0:
                    sets_favoris = {}
                    types_init = {}
                    for type in types:
                        types_init[type] = 0
                        sets_favoris[type] = []
                    for tune in tunes_favoris:
                        if types_init[tune.of_tune.type] == 3:
                            types_init[tune.of_tune.type] = 0
                            sets_favoris[tune.of_tune.type].insert(0, tune.of_tune.type)
                            final_favoris_sets.append(sets_favoris[tune.of_tune.type])
                            sets_favoris[tune.of_tune.type] = []
                        sets_favoris[tune.of_tune.type].append(tune)
                        types_init[tune.of_tune.type] = types_init[tune.of_tune.type] + 1
                    for key, final_set in sets_favoris.items():
                        if len(final_set) > 0:
                                final_set.insert(0, key)
                                final_favoris_sets.append(final_set)

                if len(tunes) > 0:
                    sets = {}
                    types_init = {}
                    for type in types:
                        types_init[type] = 0
                        sets[type] = []
                    for tune in tunes:
                        if types_init[tune.type] == 3:
                            types_init[tune.type] = 0
                            sets[tune.type].insert(0, tune.type)
                            final_tunes_sets.append(sets[tune.type])
                            sets[tune.type] = []
                        sets[tune.type].append(tune)
                        types_init[tune.type] = types_init[tune.type] + 1
                    for key, final_set in sets.items():
                        if len(final_set) > 0:
                                final_set.insert(0, key)
                                final_tunes_sets.append(final_set)
            messages.success(request, _(
                'The list of "%(list_of)s" among "%(among)s" has been generated') % {
                'list_of': list_of,
                'among': among
            })
    else:
        form = GenerateurForm()
    return render(request, 'tune/generateur.html', {'form': form,
                                                    'tunes': tunes,
                                                    'sets': final_tunes_sets,
                                                    'tunes_favoris': tunes_favoris,
                                                    'sets_favoris': final_favoris_sets,
                                                    'group': slug})


@login_required
def comparateur(request):
    tunes_en_commun = []
    mes_tunes_en_plus = []
    mes_tunes_en_moins = []
    if request.method == 'POST':
        form = CompareUserForm(request.POST)
        if form.is_valid():
            # Check if user exists
            username = form.cleaned_data["username"]
            groupname = form.cleaned_data["groupname"]
            to_compare = form.cleaned_data["to_compare"]
            try:
                if not username == "not_chosen":
                    user_to_compare = User.objects.get(username=username)
                    # Compare tunes with this user
                    if to_compare == "Mes tunes favoris appris":
                        mes_tunes_favoris = TuneFavori_user.objects.filter(of_user=request.user, status=True)
                        tunes_favoris_to_compare = TuneFavori_user.objects.filter(of_user=user_to_compare, status=True)
                    elif to_compare == "Mes tunes favoris":
                        mes_tunes_favoris = TuneFavori_user.objects.filter(of_user=request.user)
                        tunes_favoris_to_compare = TuneFavori_user.objects.filter(of_user=user_to_compare)
                    for tune_favori in mes_tunes_favoris:
                        if tunes_favoris_to_compare.filter(of_tune=tune_favori.of_tune).count() == 1:
                            tunes_en_commun.append(tune_favori)
                            tunes_favoris_to_compare = tunes_favoris_to_compare.exclude(of_tune=tune_favori.of_tune)
                        else:
                            mes_tunes_en_plus.append(tune_favori)
                    mes_tunes_en_moins = list(tunes_favoris_to_compare)
                    messages.success(request, _(
                    'The comparison of "%(to_compare)s" with user "%(username)s" is a success.') % {
                    'to_compare': to_compare,
                    'username': username
                    })
                elif not groupname == "not_chosen":
                    group_to_compare = GroupExtend.objects.get(name=groupname)
                    # Compare tunes with this user
                    if to_compare == "Mes tunes favoris appris":
                        mes_tunes_favoris = TuneFavori_user.objects.filter(of_user=request.user, status=True)
                        tunes_favoris_to_compare = TuneFavori_group.objects.filter(of_group=group_to_compare, status=True)
                    elif to_compare == "Mes tunes favoris":
                        mes_tunes_favoris = TuneFavori_user.objects.filter(of_user=request.user)
                        tunes_favoris_to_compare = TuneFavori_group.objects.filter(of_group=group_to_compare)
                    for tune_favori in mes_tunes_favoris:
                        if tunes_favoris_to_compare.filter(of_tune=tune_favori.of_tune).count() == 1:
                            tunes_en_commun.append(tune_favori)
                            tunes_favoris_to_compare = tunes_favoris_to_compare.exclude(of_tune=tune_favori.of_tune)
                        else:
                            mes_tunes_en_plus.append(tune_favori)
                    mes_tunes_en_moins = list(tunes_favoris_to_compare)
                    messages.success(request, _(
                    'The comparison of "%(to_compare)s" with group "%(groupname)s" is a success.') % {
                    'to_compare': to_compare,
                    'groupname': groupname
                    })
                else:
                    messages.error(
                        request,
                        _('The comparison of tunes has failed. An error appeared with name of the user or group')
                    )
                    return redirect('tune:comparateur')
            except User.DoesNotExist:
                messages.warning(
                    request,
                    _('The user "%(username)s" doesn\'t exist. Please enter an existing user') % {'username': username}
                )
            except GroupExtend.DoesNotExist:
                messages.warning(
                    request,
                    _(
                    'The group "%(groupname)s" doesn\'t exist. Please enter an existing group') % {'groupname': groupname}
                )
            except User.MultipleObjectsReturned:
                messages.error(
                    request,
                    _(
                    'There are several users "%(username)s". Impossible to compare Tunes.') % {'username': username})
            except GroupExtend.MultipleObjectsReturned:
                messages.error(
                    request,
                    _('There are several groups "%(groupname)s". Impossible to compare Tunes.') % {'groupname': groupname})
    else:
        form = CompareUserForm()
    return render(request, 'tune/comparateur.html', {"form": form,
                                                     "tunes_en_commun": tunes_en_commun,
                                                     "mes_tunes_en_plus": mes_tunes_en_plus,
                                                     "mes_tunes_en_moins": mes_tunes_en_moins
                                                     })


class LireTune(DetailView):
    context_object_name = "tune"
    model = Tune
    template_name = "tune/tune_lire.html"

    def get_object(self):
        tune = super(LireTune, self).get_object()
        tune.nb_vues = tune.nb_vues + 1
        path_abc = Path(settings.MEDIA_ROOT + "tune_abc/" + tune.slug + ".abc")
        path_svg = Path(settings.MEDIA_ROOT + "tune_svg/" + tune.slug + ".svg")
        path_midi = Path(settings.MEDIA_ROOT + "tune_midi/" + tune.slug + ".mid")
        temp_path = Path(settings.MEDIA_ROOT + "tune_abc/" + tune.slug + "temp.abc")
        if not path_abc.is_file():
            constructABC_from_tune(tune, path_abc, temp_path)
        if not path_svg.is_file() and settings.DEBUG == False:
            constructSVG_from_ABC(path_abc, path_svg)
        if not path_midi.is_file() and settings.DEBUG == False:
            constructMIDI_from_ABC(path_abc, path_midi, path_wav)
        tune.save()
        return tune

    def get_context_data(self, **kwargs):
        tune = super(LireTune, self).get_object()
        context = super().get_context_data(**kwargs)
        context['user_clyps'] = Audio_clyp_user_favori.objects.filter(of_tune_favori_user__of_tune=tune)
        context['group_clyps'] = Audio_clyp_group_favori.objects.filter(of_tune_favori_group__of_tune=tune)
        return context


@login_required
def tune_favori_lire(request, slug):
    try:
        tune_favori = TuneFavori_user.objects.get(slug=slug)
        if request.user.has_tune_favori(tune_favori):
            type = "user"
        else:
            messages.error(request, _('This Tune is not among your favorites !'))
            return redirect("tune:tune_liste_favoris")
    except TuneFavori_user.DoesNotExist:
        tune_favori = TuneFavori_group.objects.get(slug=slug)
        type = "group"
    messages.info(
        request,
        _('This is the page of the favorite Tune. If you wish to go to the global Tune, go there : ') +
        '''<a
                href="%(url)s"
                        class="btn-link tooltipInfo" data-toggle="tooltip"
                        title="Go to tune : %(tune)s"><span>%(favori)s</span>
                        <i class="fa fa-chevron-circle-right" aria-hidden="true"></i></a>''' % {
                                "url": reverse_lazy("tune:tune_lire", kwargs={
                                    "slug": tune_favori.of_tune.slug
                                }),
                                "tune": tune_favori.of_tune.name,
                                "favori": tune_favori.of_tune.name
        },
        extra_tags='safe'
    )
    return render(request, 'tune/tune_favori_lire.html', {
        "tune_favori": tune_favori,
        "type": type
    })


@login_required
def tune_favori_add_sound(request, slug):
    tune_favori_user = None
    tune_favori_group = None
    tune_favori = TuneFavori.objects.get(slug=slug)
    try:
        tune_favori_user = TuneFavori_user.objects.get(slug=slug)
        if not request.user.has_tune_favori(tune_favori_user):
            messages.error(request, _('This Tune is not among your favorites !'))
            return redirect("tune:tune_liste_favoris")
    except TuneFavori_user.DoesNotExist:
        tune_favori_group = TuneFavori_group.objects.get(slug=slug)
        if request.user.groupe_roles.filter(of_group=tune_favori_group.of_group).exists():
            if request.user.groupe_roles.filter(of_group=tune_favori_group.of_group).first().role == "admin":
                pass
            else:
                messages.error(request, _('Only administrators of the group can use this functionnality'))
                return redirect("user:groupe_liste")
        else:
            messages.error(request, _('Only administrators of the group can use this functionnality'))
            return redirect("user:groupe_liste")

    form = ClypForm(request.POST or None)
    if form.is_valid():
        if tune_favori_user:
            audio_clyp = Audio_clyp_user_favori()
            audio_clyp.of_tune_favori_user = tune_favori_user
        else:
            audio_clyp = Audio_clyp_group_favori()
            audio_clyp.of_tune_favori_group = tune_favori_group
        audio_clyp.description = form.cleaned_data["description"]
        audio_clyp.name = form.cleaned_data["name"]
        audio_clyp.href = form.cleaned_data["href"]
        audio_clyp.added_by = request.user
        try:
            obj = Audio_clyp.objects.get(slug=slugify(audio_clyp.href + "-" + request.user.username))
            messages.error(request, _('You have already linked this sound to another favorite'))
            return redirect("tune:tune_favori_add_sound", slug=slug)
        except Audio_clyp.DoesNotExist:
            audio_clyp.save()
        return redirect("tune:tune_favori_lire", slug=slug)

    return render(request, 'tune/tune_favori_add_sound.html', {
        "tune_favori": tune_favori,
        "form": form
    })


def createABCTune(request):

    formUpload = UploadABCFileForm(request.POST, request.FILES or None)
    formArea = TextAreaABCForm(request.POST or None)
    if formArea.is_valid():
        handle_text_area(request.POST.get("abc"), request)
        messages.success(request, _('Processus successfully ended !'))
    elif formUpload.is_valid() and request.user.is_admin:
        handle_uploaded_file(request.FILES['file'], request)
        messages.success(request, _('Processus successfully ended !'))
    else:
        print(formUpload.is_valid())

    return render(request, 'tune/new_from_abc.html', {"formArea": formArea, "formUpload": formUpload})


# class DeleteTune(LoginRequiredMixin, DeleteView):
#     model = Tune
#     context_object_name = "tune"
#     template_name = 'tune/tune_delete.html'
#     success_url = reverse_lazy('tune_liste')

#     def get_object(self, queryset=None):
#         code = self.kwargs.get('code', None)
#         return get_object_or_404(Tune, slug=code)


def switch_favori(request):
    tune_slug = request.POST.get('tune_slug', None)

    if tune_slug:
        try:
            tune_favori = TuneFavori_user.objects.get(of_user=request.user, of_tune__slug=tune_slug)
        except TuneFavori_user.DoesNotExist:
            tune_favori = None

        if tune_favori:
            tune_favori.delete()
            return HttpResponse("deleted")
        else:
            tune = Tune.objects.get(slug=tune_slug)
            create_tune_favori = TuneFavori_user(of_user=request.user, of_tune=tune)
            create_tune_favori.save()
            user = User.objects.get(id=request.user.id)
            user.tunes_favoris.add(create_tune_favori)
            return HttpResponse("added")
    return HttpResponse("unchanged")


def switch_status(request):
    tune_favori_slug = request.POST.get('tune_favori_slug', None)

    if tune_favori_slug:
        try:
            tune_favori = TuneFavori_user.objects.get(slug=tune_favori_slug, of_user=request.user)
        except TuneFavori_user.DoesNotExist:
            try:
                tune_favori = TuneFavori_group.objects.get(slug=tune_favori_slug)
                if request.user.groupe_roles.filter(of_group__slug=tune_favori.of_group.slug).exists():
                    if request.user.groupe_roles.filter(of_group__slug=tune_favori.of_group.slug).first().role == "admin":
                        pass
                    else:
                        return HttpResponse("unchanged")
                else:
                    return HttpResponse("unchanged")
            except TuneFavori_group.DoesNotExist:
                tune_favori = None

        if tune_favori:
            if tune_favori.status:
                tune_favori.status = False
                tune_favori.save()
                return HttpResponse("down")
            else:
                tune_favori.status = True
                tune_favori.save()
                return HttpResponse("up")
    return HttpResponse("unchanged")


def delete_tune_favori(request):
    tune_favori_slug = request.POST.get('tune_favori_slug', None)
    if tune_favori_slug:
        try:
            tune_favori = TuneFavori_user.objects.get(of_tune__slug=tune_favori_slug, of_user=request.user)
        except TuneFavori_user.DoesNotExist:
            try:
                tune_favori = TuneFavori_group.objects.get(of_tune__slug=tune_favori_slug)
                if not request.user.is_admin_of_this_group(request, tune_favori.of_group):
                    return HttpResponse("unchanged")
            except TuneFavori_group.DoesNotExist:
                tune_favori = None
        if tune_favori:
            tune_favori.delete()
            return HttpResponse("deleted")
    return HttpResponse("unchanged")


def delete_sound(request):
    print("lol")
    audio_slug = request.POST.get('audio_slug', None)
    if audio_slug:
        if request.user.audio_clyp_set.filter(slug=audio_slug).exists():
            audio_clyp = request.user.audio_clyp_set.get(slug=audio_slug)
            audio_clyp.delete()
            return HttpResponse("deleted")
    return HttpResponse("unchanged")
