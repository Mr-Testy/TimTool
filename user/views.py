from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, DetailView, FormView
from django.core.urlresolvers import reverse
from django.contrib.messages.views import SuccessMessageMixin
from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from django.conf import settings

from .forms import ContactForm, GroupForm, UserForm
from tune.models import Tune, TuneFavori_group
from .models import GroupExtend, UserGroupRole
from tune.views import LoginRequiredMixin


User = get_user_model()


def contact(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        sujet = form.cleaned_data['sujet']
        message = form.cleaned_data['message']
        envoyeur = form.cleaned_data['envoyeur']
        renvoi = form.cleaned_data['renvoi']
        mail_to = [settings.DEFAULT_FROM_EMAIL]
        message = message + " --- Sent by : " + envoyeur
        if renvoi:
            mail_to.append(envoyeur)

        send_mail(sujet,
                  message,
                  envoyeur,
                  mail_to,
                  fail_silently=True,
                  )
        messages.success(request, _('Your email has successfully been sent !'))
        return redirect("accueil")

    return render(request, 'user/contact.html', locals())


@login_required
def profile(request):
    tunes_added = Tune.objects.filter(added_by=request.user)
    groupes_added = GroupExtend.objects.filter(created_by=request.user)
    return render(request, 'user/profile.html', {'tunes_added': tunes_added, 'groupes_added': groupes_added})


def toggle_menu(request):
    boolean = request.POST.get('boolean', None)
    if boolean == "true":
        request.session['toggle_menu'] = True
        return HttpResponse("true")
    else:
        request.session['toggle_menu'] = False
        return HttpResponse("false")


class ListeGroups(ListView):
    model = GroupExtend
    context_object_name = "groups"
    template_name = "user/groupe_liste.html"
    paginate_by = 200

    def get_queryset(self):
        q_name = self.request.GET.get("q_name", None)
        groups = GroupExtend.objects.all()
        if q_name:
            groups = groups.filter(name__icontains=q_name)
        if q_name:
            messages.success(self.request, _('The following filter has been applied : "name" contains "%(name)s"') % {
                'name': q_name,
                })
        return groups


class CreateGroup(SuccessMessageMixin, LoginRequiredMixin, FormView):
    template_name = 'user/groupe_new.html'
    form_class = GroupForm

    def form_valid(self, form):
        group = ""
        try:
            group = GroupExtend.objects.get(name=form.cleaned_data.get("name"))
        except GroupExtend.DoesNotExist:
            group = GroupExtend.objects.create_groupextend(name=form.cleaned_data.get("name"), description=form.cleaned_data.get("description"), created_by=self.request.user)
            new_user_group_role = UserGroupRole(of_group=group, of_user=self.request.user, role="admin")
            new_user_group_role.save()
            group.user_roles.add(new_user_group_role)
            self.request.user.groupe_roles.add(new_user_group_role)
            messages.success(self.request, _('The group "%(groupname)s" has been created.') % {
                'groupname': group.name
                             })
            return redirect("user:groupe_liste")
        messages.warning(
            self.request, _('The group "%(groupname)s" already exists !') % {
                'groupname': group.name
            })
        return render(self.request, "user/groupe_new.html", {"form": form})

    def get_success_url(self):
        return reverse('user:groupe_liste')


class LireGroup(DetailView):
    context_object_name = "group"
    model = GroupExtend
    template_name = "user/groupe_lire.html"

    def get_object(self):
        group = super(LireGroup, self).get_object()
        group.nb_vues = group.nb_vues + 1
        group.save()
        return group


@login_required
def updateGroup(request, slug):
    group = GroupExtend.objects.get(slug=slug)
    if not request.user.is_admin_of_this_group(request, group):
        return redirect("user:groupe_liste")
    form = GroupForm(request.POST or None, initial={'name': group.name, "description": group.description})
    if form.is_valid():
        if slugify(form.cleaned_data["name"]) != slug:
            try:
                group2 = GroupExtend.objects.get(name=form.cleaned_data.get("name"))
                messages.warning(request, _('The group "%(groupname)s" already exists !') % {'groupname': form.cleaned_data.get("name")})
                return render(request, 'user/groupe_update.html', {"form": form, "group": group})
            except GroupExtend.DoesNotExist:
                group.name = form.cleaned_data["name"]
                group.slug = slugify(group.name)
        group.description = form.cleaned_data["description"]
        group.save()
        messages.success(request, _('The group "%(groupname)s" has been updated') % {'groupname': group.name})
        return redirect('user:groupe_lire', slug=group.slug)
    return render(request, 'user/groupe_update.html', {"form": form, "group": group})


@login_required
def updateGroupRoles(request, slug):
    group = GroupExtend.objects.get(slug=slug)
    if not request.user.is_admin_of_this_group(request, group):
        return redirect("user:groupe_liste")
    return render(request, 'user/groupe_update_roles.html', {"group": group})


@login_required
def updateProfil(request):
    user = User.objects.get(username=request.user.username)
    form = UserForm(request.POST or None, initial={'username': user.username, "email": user.email})
    if form.is_valid():
        if form.cleaned_data["username"] != user.username:
            try:
                user = User.objects.get(username=form.cleaned_data.get("username"))
                messages.warning(request, _('The user "%(username)s" already exists') % {'username': user.username})
                return render(request, 'user/profil_update.html', {"form": form, "user": user})
            except User.DoesNotExist:
                user.username = form.cleaned_data["username"]
        # user.first_name = form.cleaned_data["first_name"]
        # user.last_name = form.cleaned_data["last_name"]
        user.email = form.cleaned_data["email"]
        user.save()
        messages.success(request, _('Your profile has been updated'))
        return redirect('user:profile')
    return render(request, 'user/profil_update.html', {"form": form})


@login_required
def joinGroup(request):
    group = request.POST.get('groupe_id', None)
    group_to_add = GroupExtend.objects.get(id=group)
    new_user_group_role = UserGroupRole(of_group=group_to_add, of_user=request.user, role="member")
    new_user_group_role.save()
    request.user.groupe_roles.add(new_user_group_role)
    group_to_add.user_roles.add(new_user_group_role)
    messages.success(request, _('You have joined the group'))
    return redirect('user:groupe_lire', slug=group_to_add.slug)


@login_required
def leaveGroup(request):
    group = request.POST.get('groupe_id', None)
    group_to_leave = GroupExtend.objects.get(id=group)
    if request.user.groupe_roles.get(of_group=group_to_leave, of_user=request.user).role == "admin":
        messages.error(request, _('You can\'t leave this group because you are the last administrator'))
    else:
        user_group_role = UserGroupRole.objects.get(of_group=group_to_leave, of_user=request.user)
        user_group_role.delete()
        messages.success(request, _('You left this group'))
    return redirect('user:groupe_lire', slug=group_to_leave.slug)


@login_required
def add_favoris_to_group(request, slug):
    group = GroupExtend.objects.get(slug=slug)
    if not request.user.is_admin_of_this_group(request, group):
        return redirect("user:groupe_liste")
    return render(request, 'user/groupe_add_favoris.html', {"group": group})


@login_required
def groupe_switch_favori(request):
    tune_slug = request.POST.get('tune_slug', None)
    groupe_id = request.POST.get('groupe_id', None)
    if tune_slug and groupe_id:
        try:
            tune_favori = TuneFavori_group.objects.get(of_group=groupe_id, of_tune__slug=tune_slug)
            if not request.user.is_admin_of_this_group(request, tune_favori.of_group):
                return HttpResponse("unchanged")
        except TuneFavori_group.DoesNotExist:
            tune_favori = None

        if tune_favori:
            tune_favori.delete()
            return HttpResponse("deleted")
        else:
            tune = Tune.objects.get(slug=tune_slug)
            group = GroupExtend.objects.get(id=groupe_id)
            create_tune_favori = TuneFavori_group(of_group=group, of_tune=tune)
            create_tune_favori.save()
            group.tunes_favoris.add(create_tune_favori)
            json = {"status": "added",
                    "tune_name": create_tune_favori.of_tune.name,
                    "tune_type": create_tune_favori.of_tune.type,
                    "tune_key": create_tune_favori.of_tune.key,
                    "tune_favori_id": create_tune_favori.id
                    }
            return JsonResponse(json)
    return HttpResponse("unchanged")


@login_required
def groupe_switch_role(request):
    user_role_id = request.POST.get('user_role_id')
    user_role_value = request.POST.get('user_role_value')
    myself = request.POST.get('myself')
    if user_role_id and (user_role_value == "Admin" or user_role_value == "Member"):
        user_role = UserGroupRole.objects.get(id=user_role_id)
        if not request.user.is_admin_of_this_group(request, user_role.of_group):
            return HttpResponse("unauthorized")
        if user_role.of_user == request.user and myself == "False":
            return HttpResponse("warning")
        if UserGroupRole.objects.filter(of_group=user_role.of_group, role="admin").count() < 2 and user_role_value == "Member":
            return HttpResponse("last_one")
        user_role.role = user_role_value.lower()
        user_role.save()
        return HttpResponse("updated")
    return HttpResponse("unchanged")


class ListeUserGroups(ListView):
    model = GroupExtend
    context_object_name = "groups"
    template_name = "user/user_groupe_liste.html"
    paginate_by = 200

    def get_queryset(self):
        q_name = self.request.GET.get("q_name", None)
        groups = GroupExtend.objects.filter(user_roles__of_user=self.request.user)
        if q_name:
            groups = groups.filter(name__icontains=q_name)
        if q_name:
            messages.success(self.request, _('The following filter has been applied : "name" contains "%(name)s"') % {
                'name': q_name,
                })
        return groups
