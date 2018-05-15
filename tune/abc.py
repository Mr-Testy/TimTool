from .models import ABCTune, Tune, Title, Composer
from django.template.defaultfilters import slugify
from django.contrib import messages
from os import remove, rename
from subprocess import run
from django.core import serializers
from django.db.models import Q
from django.utils.translation import ugettext as _

def handle_uploaded_file(file, version, request, is_from):
    content = file.readlines()
    all_abc = []
    flag = False
    for line in content:
        if not flag:
            line = line.decode("UTF-8").strip("\r\n")
            line = line.split(":")
            if line[0] == "X":
                all_abc.append(ABCTune(X=int(line[1])))
            elif line[0] == "T":
                if all_abc[-1].T == "":
                    all_abc[-1].T = line[1]
                elif not all_abc[-1].other_title:
                    all_abc[-1].other_title = line[1]
                elif not all_abc[-1].other_title2:
                    all_abc[-1].other_title2 = line[1]
            elif line[0] == "R":
                all_abc[-1].R = line[1]
            elif line[0] == "C":
                if all_abc[-1].C == "":
                    all_abc[-1].C = line[1]
                elif not all_abc[-1].other_composer:
                    all_abc[-1].other_composer = line[1]
                elif not all_abc[-1].other_composer2:
                    all_abc[-1].other_composer2 = line[1]
            elif line[0] == "S":
                all_abc[-1].S = line[1]
            elif line[0] == "H" and not all_abc[-1].H:
                all_abc[-1].H = line[1]
            elif line[0] == "H":
                all_abc[-1].H = all_abc[-1].H + "\r\n" + line[1]
            elif line[0] == "N" and not all_abc[-1].N:
                all_abc[-1].N = line[1]
            elif line[0] == "N":
                all_abc[-1].N = all_abc[-1].N + "\r\n" + line[1]
            elif line[0] == "D" and not all_abc[-1].D:
                all_abc[-1].D = line[1]
            elif line[0] == "D":
                all_abc[-1].D = all_abc[-1].D + "\r\n" + line[1]
            elif line[0] == "Z":
                all_abc[-1].Z = line[1]
            elif line[0] == "M":
                all_abc[-1].M = line[1]
            elif line[0] == "L":
                all_abc[-1].L = line[1]
            elif line[0] == "Q":
                all_abc[-1].Q = line[1]
            elif line[0] == "K":
                all_abc[-1].K = line[1]
                flag = True
        else:
            line = line.decode("UTF-8")
            if len(line) > 4:
                if line[0] == "W" and not all_abc[-1].W:
                    all_abc[-1].W = line[1]
                elif line[0] == "W":
                    all_abc[-1].W = all_abc[-1].W + "\r\n" + line[1]
                else:
                    all_abc[-1].content = all_abc[-1].content + line
            else:
                flag = False

    for abc in all_abc:
        if abc.T and abc.K and abc.R and abc.content:
            slug = slugify(abc.T + "-" + abc.K + "-" + abc.R)
            if abc.other_title:
                slug2 = slugify(abc.other_title + "-" + abc.K + "-" + abc.R)
            else:
                slug2 = ""
            if abc.other_title2:
                slug3 = slugify(abc.other_title2 + "-" + abc.K + "-" + abc.R)
            else:
                slug3 = ""
            titles = Title.objects.filter(Q(slug=slug) | Q(slug=slug2) | Q(slug=slug3))

            if titles.count() > 0:
                for title in titles:
                    messages.info(
                    request,
                    _('The Title "%(title)s" has been found !') % {'title': title.slug}
                    )

                    new_title, created = Title.objects.get_or_create(
                        slug=slug, defaults={'belong_to_tune': title.belong_to_tune, 'name': abc.T})
                    if created:
                        messages.success(request, _('The title "%(title)s" has been created') % {'title': new_title.slug})

                    if abc.other_title:
                        new_title2, created2 = Title.objects.get_or_create(
                            slug=slug2, defaults={'belong_to_tune': title.belong_to_tune, 'name': abc.other_title})
                        if created2:
                            messages.success(request, _('The title "%(title)s" has been created') % {'title': new_title2.slug})

                    if abc.other_title2:
                        new_title3, created3 = Title.objects.get_or_create(
                            slug=slug3, defaults={'belong_to_tune': title.belong_to_tune, 'name': abc.other_title2})
                        if created3:
                            messages.success(request, _('The title "%(title)s" has been created') % {'title': new_title3.slug})

                    if abc.C:
                        comp, created = Composer.objects.get_or_create(
                            slug=slugify(abc.C), defaults={'name': abc.C})
                        if created:
                            comp.composed_tunes.add(title.belong_to_tune)
                            messages.success(request, _('The composer "%(name)s" has been created') % {'name': comp.name})

                    if abc.other_composer:
                        comp2, created2 = Composer.objects.get_or_create(
                            slug=slugify(abc.other_composer), defaults={'name': abc.other_composer})
                        if created2:
                            comp2.composed_tunes.add(title.belong_to_tune)
                            messages.success(request, _('The composer "%(name)s" has been created') % {'name': comp2.name})

                    if abc.other_composer2:
                        comp3, created3 = Composer.objects.get_or_create(
                            slug=slugify(abc.other_composer2), defaults={'name': abc.other_composer2})
                        if created3:
                            comp3.composed_tunes.add(title.belong_to_tune)
                            messages.success(request, _('The composer "%(name)s" has been created') % {'name': comp3.name})

                    if title.belong_to_tune.abcs.filter(version__iexact=version).count() == 0:
                        abc.tune = title.belong_to_tune
                        abc.version = version
                        if not is_from == "Tunebook":
                            # Requêter le bon user et l'ajouter à la version du Tune
                            pass
                        abc.save()
                        messages.info(
                            request,
                            _('The .abc version "%(version)s" of Tune "%(tune)s" has been added !') % {
                            'version': abc.version,
                            'tune': title.belong_to_tune.slug
                            }
                        )
                    else:
                        messages.warning(
                            request,
                            _('The .abc version "%(version)s" of Tune "%(tune)s" already exists !') % {
                            'version': version,
                            'tune': title.belong_to_tune.slug
                            }
                        )
            else:
                tune = Tune()
                tune.name = abc.T
                tune.key = abc.K
                tune.type = abc.R
                tune.added_by = request.user
                tune.save()
                messages.success(request, _('The tune "%(tune)s" a has been created') % {'tune': tune.slug})
                abc.tune = tune
                abc.version = version
                abc.save()
                messages.info(
                    request,
                    _('The .abc version "%(version)s" of Tune "%(tune)s" has been added !') % {
                    'version': abc.version,
                    'tune': tune.slug
                    }
                )
                title = Title(name=abc.T, slug=slug)
                title.belong_to_tune = tune
                title.save()
                messages.success(request, _('The title "%(title)s" has been created') % {'title': title.slug})
                if abc.other_title:
                    title2 = Title(name=abc.other_title, slug=slug2)
                    title2.belong_to_tune = tune
                    title2.save()
                    messages.success(request, _('The title "%(title)s" has been created') % {'title': title2.slug})
                if abc.other_title2:
                    title3 = Title(name=abc.other_title2, slug=slug3)
                    title3.belong_to_tune = tune
                    title3.save()
                    messages.success(request, _('The title "%(title)s" has been created') % {'title': title3.slug})

                if abc.C:
                    comp, created = Composer.objects.get_or_create(
                        slug=slugify(abc.C), defaults={'name': abc.C})
                    if created:
                        comp.composed_tunes.add(tune)
                        messages.success(request, _('The composer "%(name)s" has been created') % {'name': comp.name})

                if abc.other_composer:
                    comp2, created2 = Composer.objects.get_or_create(
                        slug=slugify(abc.other_composer), defaults={'name': abc.other_composer})
                    if created2:
                        comp2.composed_tunes.add(tune)
                        messages.success(request, _('The composer "%(name)s" has been created') % {'name': comp2.name})

                if abc.other_composer2:
                    comp3, created3 = Composer.objects.get_or_create(
                        slug=slugify(abc.other_composer2), defaults={'name': abc.other_composer2})
                    if created3:
                        comp3.composed_tunes.add(tune)
                        messages.success(request, _('The composer "%(name)s" has been created') % {'name': comp3.name})

        else:
            messages.error(request, "abc incomplet ou erroné")


def handle_text_area(str, request):
    content = str.splitlines(True)
    all_abc = []
    flag = False
    for line in content:
        if not flag:
            line = line.strip("\r\n")
            line = line.split(":")
            if line[0] == "X":
                all_abc.append(ABCTune(X=int(line[1])))
            elif line[0] == "T":
                if all_abc[-1].T == "":
                    all_abc[-1].T = line[1]
                elif not all_abc[-1].other_title:
                    all_abc[-1].other_title = line[1]
                elif not all_abc[-1].other_title2:
                    all_abc[-1].other_title2 = line[1]
            elif line[0] == "R":
                all_abc[-1].R = line[1]
            elif line[0] == "C":
                if all_abc[-1].C == "":
                    all_abc[-1].C = line[1]
                elif not all_abc[-1].other_composer:
                    all_abc[-1].other_composer = line[1]
                elif not all_abc[-1].other_composer2:
                    all_abc[-1].other_composer2 = line[1]
            elif line[0] == "S":
                all_abc[-1].S = line[1]
            elif line[0] == "H":
                all_abc[-1].H = all_abc[-1].H + "\r\n" + line[1]
            elif line[0] == "N":
                all_abc[-1].N = all_abc[-1].N + "\r\n" + line[1]
            elif line[0] == "D":
                all_abc[-1].D = all_abc[-1].D + "\r\n" + line[1]
            elif line[0] == "Z":
                all_abc[-1].Z = line[1]
            elif line[0] == "M":
                all_abc[-1].M = line[1]
            elif line[0] == "L":
                all_abc[-1].L = line[1]
            elif line[0] == "Q":
                all_abc[-1].Q = line[1]
            elif line[0] == "K":
                all_abc[-1].K = line[1]
                flag = True
        else:
            if len(line) > 4:
                if line[0] == "W":
                    all_abc[-1].W = all_abc[-1].W + "\r\n" + line[1]
                else:
                    all_abc[-1].content = all_abc[-1].content + line
            else:
                flag = False

    for abc in all_abc:
        if abc.T and abc.K and abc.R and abc.content:
            try:
                slug = slugify(abc.T + "-" + abc.K + "-" + abc.R)
                tune = Tune.objects.get(slug=slug)
                messages.warning(request, "le tune " + slug + " existe déjà")
            except Tune.DoesNotExist:
                abc.save()
                tune = Tune()
                tune.name = abc.T
                tune.key = abc.K
                tune.type = abc.R
                tune.description = abc.H
                tune.added_by = request.user
                tune.abc = abc
                tune.save()
                messages.success(request, "le tune " + tune.slug + " a bien été créé")
        else:
            messages.error(request, "abc incomplet ou erroné. Les champs T: (titre), K: (tonalité) et R: (type) sont obligatoires")


def constructABC_from_abc(abc, path, temp_path):
    file = open(str(temp_path), 'w')
    file.write("X:" + str(abc.id) + "\n")
    if abc.T:
        file.write("T:" + abc.T + "\n")
    if abc.other_title:
        file.write("T:" + abc.other_title + "\n")
    if abc.other_title2:
        file.write("T:" + abc.other_title2 + "\n")
    if abc.R:
        file.write("R:" + abc.R + "\n")
    if abc.C:
        file.write("C:" + abc.C + "\n")
    if abc.other_composer:
        file.write("C:" + abc.other_composer + "\n")
    if abc.other_composer2:
        file.write("C:" + abc.other_composer2 + "\n")
    if abc.Z:
        file.write("Z:" + abc.Z + "\n")
    if abc.N:
        file.write("N:" + abc.N + "\n")
    if abc.M:
        file.write("M:" + abc.M + "\n")
    if abc.L:
        file.write("L:" + abc.L + "\n")
    if abc.Q:
        file.write("Q:" + abc.Q + "\n")
    if abc.K:
        file.write("K:" + abc.K + "\n")
    file.write(abc.content)
    if abc.W:
        file.write("W:" + abc.W + "\n")
    file.close()
    with open(str(temp_path), 'r+') as infile, open(str(path), 'w') as outfile:
        for line in infile:
            if not line.isspace():
                outfile.write(line)
    remove(str(temp_path))


def constructSVG_from_ABC(path_abc, path_svg):
    run(["abcm2ps", "-g", str(path_abc), "-O", str(path_svg)])
    rename(str(path_svg).replace(".svg", "001.svg"), str(path_svg))


def constructMIDI_from_ABC(path_abc, path_midi):
    run(["abc2midi", str(path_abc), "-o", str(path_midi)])
