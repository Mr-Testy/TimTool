from .models import ABCTune, Tune
from django.template.defaultfilters import slugify
from django.contrib import messages


def handle_uploaded_file(file, request):
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
                elif all_abc[-1].other_title == "":
                    all_abc[-1].other_title = line[1]
            elif line[0] == "R":
                all_abc[-1].R = line[1]
            elif line[0] == "C":
                all_abc[-1].C = line[1]
            elif line[0] == "S":
                all_abc[-1].S = line[1]
            elif line[0] == "H":
                all_abc[-1].H = all_abc[-1].H = all_abc[-1].H + "\r\n" + line[1]
            elif line[0] == "D":
                all_abc[-1].D = all_abc[-1].D = all_abc[-1].D + "\r\n" + line[1]
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
                elif all_abc[-1].other_title == "":
                    all_abc[-1].other_title = line[1]
            elif line[0] == "R":
                all_abc[-1].R = line[1]
            elif line[0] == "C":
                all_abc[-1].C = line[1]
            elif line[0] == "S":
                all_abc[-1].S = line[1]
            elif line[0] == "H":
                all_abc[-1].H = all_abc[-1].H = all_abc[-1].H + "\r\n" + line[1]
            elif line[0] == "D":
                all_abc[-1].D = all_abc[-1].D = all_abc[-1].D + "\r\n" + line[1]
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
