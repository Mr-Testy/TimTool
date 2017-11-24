//recupération de chemin de la page courante
var CheminComplet = document.location.href;
var CheminRepertoire = CheminComplet.substring(0, CheminComplet.lastIndexOf("/"));
var NomDuFichier = CheminComplet.substring(CheminComplet.lastIndexOf("/") + 1);

$(document).ready(function(e) {
    var $input = $('#refreshPrevious');
    $input.val() == 'yes' ? location.reload(true) : $input.val('yes');
});

//Save messages personnel pour chaque élement du tableau de de mes favoris
$(function () {
    //Pour chaque élement du tableau
    $(".blocNote").each(function () {
        //A chaque changement de chaque element
        $(this).click(function () {
            var $object = $(this);
            var $commentairePersonnel = $object.nextAll(".idPersonalDescription").val();
            var $idTuneFavori = $object.nextAll(".idTuneFavori").val();

            $.confirm({
                title: 'Bloc Note Personel',
                columnClass: 'medium',
                type: 'dark',
                content: '' +
                        '<div class="form-group">' +
                        '<label>Description personnelle du Tune :</label>' +
                        '<textarea class="myPersonalDescription" rows="6" cols="100">' + $commentairePersonnel + '</textarea>' +
                        '</div>',
                buttons: {
                    Sauvegarder: {
                        btnClass: 'btn-dark',
                        action: function () {
                            $commentairePersonnel = this.$content.find('.myPersonalDescription').val();
                            $.ajax({
                                type: "POST",
                                url: Routing.generate('testy_timtool_ajax_blocNote'),
                                data: {
                                    idTuneFavori: $idTuneFavori,
                                    commentairePersonnel: $commentairePersonnel
                                },
                                beforeSend: function () {
                                    $object.nextAll(".idWaiting").show();
                                },
                                complete: function () {
                                    $object.nextAll(".idWaiting").hide();
                                },
                                success: function (data) {
                                    if (data == 'not_found') {
                                        $object.nextAll(".idPersonalDescription").val("Tune Supprimé");
                                        $object.html("Tune Supprimé");
                                        $object.addClass("fa fa-exclamation-triangle");
                                        $object.attr("data-original-title", "Le Tune a été supprimé, appuyer sur F5 pour rafraichir la page");
                                        $object.nextAll(".idShow").show();
                                        $object.nextAll(".idShow").text("Tune supprimé");
                                        $object.nextAll(".idShow").fadeOut(3000);
                                    } else {
                                        $object.nextAll(".idPersonalDescription").val($commentairePersonnel);
                                        $object.html($commentairePersonnel);
                                        $object.attr("data-original-title", data);
                                        $object.nextAll(".idShow").show();
                                        $object.nextAll(".idShow").text("Modifié");
                                        $object.nextAll(".idShow").fadeOut(3000);
                                    }
                                }
                            });
                        }
                    },
                    Annuler: function () {
                    }
                }
            });
        });
    });
});


//Change And Save status of the icon on favori
$(function () {
    //Pour chaque élement du tableau
    $(".status").each(function () {
        //A chaque changement de chaque element
        $(this).children().eq(1).click(function () {
            var $status = $(this).children().hasClass("fa-thumbs-up") ? 0 : 1;
            var $idTuneFavori = $(this).prev().val();
            var $object = $(this);

            $.ajax({
                type: "POST",
                url: Routing.generate('testy_timtool_ajax_status'),
                data: {
                    idTuneFavori: $idTuneFavori,
                    status: $status
                },
                beforeSend: function () {
                    $object.next().next().show();
                },
                complete: function () {
                    $object.next().next().hide();
                },
                success: function (data) {
                    if (data == 'true') {
                        $object.children().addClass("fa-thumbs-up").addClass("status");
                        $object.children().removeClass("fa-thumbs-down");
                        $object.parent().attr("data-original-title", "Je le connais !");
                        $object.next().show();
                        $object.next().text("Appris !");
                        $object.next().fadeOut(3000);
                    } else if (data == 'false') {
                        $object.children().addClass("fa-thumbs-down").addClass("status");
                        $object.children().removeClass("fa-thumbs-up");
                        $object.parent().attr("data-original-title", "Je ne le connais pas !");
                        $object.next().show();
                        $object.next().text("Oublié !");
                        $object.next().fadeOut(3000);
                    } else if (data == 'not_found') {
                        $object.children().addClass("fa-exclamation-triangle").addClass("status");
                        $object.children().removeClass("fa-thumbs-up").removeClass("fa-thumbs-down");
                        $object.parent().attr("data-original-title", "Le Tune a été supprimé, appuyer sur F5 pour rafraichir la page");
                        $object.next().show();
                        $object.next().text("Tune supprimé");
                        $object.next().fadeOut(3000);
                    }
                }
            });
        });
    });
});

//Add Or Remove Tune Favori Anywhere
$(function () {
    //Pour chaque coeur
    $(".favori").each(function () {
        //A chaque changement de chaque element
        $(this).click(function () {
            var $object = $(this);
            var $tune = $object.nextAll(".idTune").val();
            var $user = $object.nextAll(".idUser").val();
            var $src = $object.children().hasClass("fa-heart-o") ? 0 : 1;
            var $ajax = true;
            if ($object.hasClass("tuneFavoriWarning") && $src == 1) {
                $ajax = false;
                $.confirm({
                    title: 'Danger',
                    content: 'Retirer ce favori signifie effacer toutes les données personnelles liées à ce Tune. Voulez-vous poursuivre ?',
                    columnClass: 'medium',
                    type: 'red',
                    buttons: {

                        Poursuivre: {
                            btnClass: 'btn-red',
                            action: function () {
                                $.ajax({
                                    type: "POST",
                                    url: Routing.generate('testy_timtool_ajax_favori'),
                                    data: {
                                        idTune: $tune,
                                        idUser: $user,
                                        src: $src
                                    },
                                    beforeSend: function () {
                                        $object.nextAll(".idWaiting").show();
                                    },
                                    complete: function () {
                                        $object.nextAll(".idWaiting").hide();
                                    },
                                    success: function () {
                                        if ($src == 1) {
                                            $object.children().addClass("fa-heart-o").addClass("favori");
                                            $object.children().removeClass("fa-heart");
                                            $object.attr("data-original-title", "Tune retiré de vos favoris");
                                            $object.nextAll(".idShow").show();
                                            $object.nextAll(".idShow").text("Retiré");
                                            $object.nextAll(".idShow").fadeOut(3000);
                                        } else if ($src == 0) {
                                            $object.children().addClass("fa-heart").addClass("favori");
                                            $object.children().removeClass("fa-heart-o");
                                            $object.attr("data-original-title", "Tune ajouté à vos favoris");
                                            $object.nextAll(".idShow").show();
                                            $object.nextAll(".idShow").text("Ajouté");
                                            $object.nextAll(".idShow").fadeOut(3000);
                                        }
                                    }
                                });
                            }
                        },
                        Annuler: function () {
                        }
                    }
                });
            }
            if ($ajax == true) {
                $.ajax({
                    type: "POST",
                    url: Routing.generate('testy_timtool_ajax_favori'),
                    data: {
                        idTune: $tune,
                        idUser: $user,
                        src: $src
                    },
                    beforeSend: function () {
                        $object.nextAll(".idWaiting").show();
                    },
                    complete: function () {
                        $object.nextAll(".idWaiting").hide();
                    },
                    success: function () {
                        if ($src == 1) {
                            $object.children().addClass("fa-heart-o").addClass("favori");
                            $object.children().removeClass("fa-heart");
                            $object.attr("data-original-title", "Tune retiré de vos favoris");
                            $object.nextAll(".idShow").show();
                            $object.nextAll(".idShow").text("Retiré");
                            $object.nextAll(".idShow").fadeOut(3000);
                        } else if ($src == 0) {
                            $object.children().addClass("fa-heart").addClass("favori");
                            $object.children().removeClass("fa-heart-o");
                            $object.attr("data-original-title", "Tune ajouté à vos favoris");
                            $object.nextAll(".idShow").show();
                            $object.nextAll(".idShow").text("Ajouté");
                            $object.nextAll(".idShow").fadeOut(3000);
                        }
                    }
                });
            }
        });
    });
});

//Confirmation before delete
$(function () {
    //Pour chaque delete
    $(".delete").each(function () {
        $(this).click(function () {
            var submit = $(this);
            $.confirm({
                title: 'Supprimer "' + $(this).next().next().next().val() + '" ?',
                content: 'Veux-tu vraiment supprimer le Tune "' + $(this).next().next().next().val() + '" ? Cela supprimera définitivement le tune ainsi que toutes les informations associées. Ce tune sera supprimé des listes de favoris de tous les utilisateurs.',
                columnClass: 'medium',
                type: 'orange',
                buttons: {
                    Supprimer: function () {
                        submit.parent().submit();
                    },
                    Annuler: function () {
                    }
                }
            });
        });
    });
});

//Rejoindre un groupe
$(function () {
    //Pour chaque delete
    $("#joinGroup").each(function () {
        $(this).click(function (e) {
            e.preventDefault();
            $.confirm({
                title: 'Rejoindre ce groupe ?',
                content: 'Veux-tu rejoindre ce groupe ?',
                columnClass: 'medium',
                type: 'green',
                buttons: {
                    Oui: function () {
                        $("#addMeToThisGroup").submit();
                    },
                    Non: function () {
                    }
                }
            });
        });
    });
});

//Quitter un groupe
$(function () {
    //Pour chaque delete
    $("#leaveGroup").each(function () {
        $(this).click(function (e) {
            e.preventDefault();
            $.confirm({
                title: 'Quitter ce groupe ?',
                content: 'Veux-tu quitter ce groupe ?',
                columnClass: 'medium',
                type: 'red',
                buttons: {
                    Oui: function () {
                        $("#removeMeFromThisGroup").submit();
                    },
                    Non: function () {
                    }
                }
            });
        });
    });
});

//Message d'information user non connecté
$(function () {
    //Pour chaque delete
    $("#notRemembered").each(function () {
        $(this).click(function (e) {
            $.alert({
                title: 'Vous n\'êtes pas connecté',
                content: 'Afin de bénéficier de toutes les fonctionnalités du site, connectez-vous via le formulaire de connection en haut à droite !',
                columnClass: 'medium',
                type: 'orange'
            });
        });
    });
});

//Générer Tunes Aléatoires
$(function () {
    $("#randomTune").click(function () {
        $(".generated").empty();
        $(".generated").html('Generating... <i class="fa fa-cog fa-spin fa-lg fa-fw"></i>');
        $.post(Routing.generate('testy_timtool_ajax_randomTune'))
                .done(function (data) {
                    $(".generated").empty();
                    $(".generated").html(data);
                });
    });
});
$(function () {
    $("#randomSets").click(function () {
        $(".generated").empty();
        $(".generated").html('Generating... <i class="fa fa-cog fa-spin fa-lg fa-fw"></i>');
        $.post(Routing.generate('testy_timtool_ajax_randomSets'))
                .done(function (data) {
                    $(".generated").empty();
                    $(".generated").html(data);
                });
    });
});
$(function () {
    $("#randomTunes").click(function () {
        $(".generated").empty();
        $(".generated").html('Generating... <i class="fa fa-cog fa-spin fa-lg fa-fw"></i>');
        $.post(Routing.generate('testy_timtool_ajax_randomTunes'))
                .done(function (data) {
                    $(".generated").empty();
                    $(".generated").html(data);
                });
    });
});

// Vérification du formulaire lorsqu'on submit
$(document).ready(function () {
    $('#ajoutTune').click(function (e) {
        e.preventDefault(); // on annule la fonction par défaut du bouton
        // d'envoi
        $object = $(this);
        $tuneTonalite = $('#tuneTonalite').val();
        $tuneMode = $('#tuneMode').val();
        $tuneType = $('#tuneType').val();
        $tuneKeyMode = $tuneTonalite + $tuneMode;
        $tuneName = $('#tuneName').val();
        if ($tuneName.match("^[a-zA-Z0-9\s']{1,50}$")) {
            if ($tuneTonalite != "false" && $tuneMode != "false" && $tuneType != "false") {

                $.ajax({
                    type: "POST",
                    url: Routing.generate('testy_timtool_ajax_addTune'),
                    data: {
                        tuneType: $tuneType,
                        tuneKeyMode: $tuneKeyMode,
                        tuneName: $tuneName
                    },
                    beforeSend: function () {
                        $object.next().next().show();
                    },
                    complete: function () {
                        $object.next().next().hide();
                    },
                    success: function (data) {
                        if (data == "false") {
                            $('#ajoutTuneForm').submit();
                        } else {
                            $.alert({
                                title: 'Ce Tune existe déjà !',
                                content: 'Veuillez utiliser le tune existant ou modifier les valeurs entrées.',
                                type: 'red'
                            });
                        }
                    }
                });
            } else {
                $.alert({
                    title: 'Veuillez completer tous les champs avant d\'ajouter le Tune',
                    content: '',
                    type: 'red'
                });
            }
        } else {
            if ($tuneName == "") {
                $.alert({
                    title: 'Le champ Nom du tune ne peut être vide',
                    content: 'Verifiez le champ "Nom du Tune"',
                    type: 'red'
                });
            } else {
                $.alert({
                    title: 'Les caractères spéciaux sont interdits',
                    content: 'Verifiez le champ "Nom du Tune"',
                    type: 'red'
                });
            }
        }
    });
});

//Vérification de la recherche de Tune
$(document).ready(function () {
    $('#searchTune').click(function (e) {
        e.preventDefault(); // on annule la fonction par défaut du bouton
        // d'envoi
        if ($('#inputSearchTune').val().match("^[a-zA-Z0-9 ']{1,50}$")) {
            $('#searchTuneForm').submit();
        } else {
            if ($('#inputSearchTune').val() == "") {
                $.alert({
                    title: 'Le champ de recherche de Tune ne peut être vide',
                    content: 'Verifiez le champ de recherche',
                    type: 'red'
                });
            } else {
                $.alert({
                    title: 'Les caractères spéciaux sont interdits',
                    content: 'Verifiez le champ de recherche',
                    type: 'red'
                });
            }
        }
    });
});

//Background
var jumboHeight = $('.jumbotron').outerHeight();
function parallax() {
    var scrolled = $(window).scrollTop();
    $('.bg').css('height', (jumboHeight - scrolled) + 'px');
}
$(window).scroll(function (e) {
    parallax();
});

//Ajout des tooltips
$(function () {
    $(".tooltipInfo").tooltip({trigger: 'hover'});
});

// Page Loader
$(window).on('load', function () {
    // Animate loader off screen
    $(".loaderPage").hide();
});
