// ADD FAVORI TO USER
var switchFavori = function(event){
        event.preventDefault();
        var element = $(this);
        element.append("<i class='fa fa-spinner fa-spin fa-fw'></i>");
        $.ajax({
            url : '/tune/switch_favori/',
            type : 'POST',
            data : {
                tune_slug : element.attr("data-id")
                },
             complete: function () {
                     element.find("i:last").remove();
                 },   
            success : function(response){
            if (response == "added"){
                element.children().addClass("fa-heart").removeClass("fa-heart-o");
                element.attr("data-original-title", gettext('Tune added to your favorites'));
            }
            else if (response == "deleted"){
                element.children().addClass("fa-heart-o").removeClass("fa-heart");
                element.attr("data-original-title", gettext('Tune removed from your favorites'));
            }
            else {
                }
            }
            });
        };
$(function () {
    $('.favori').click(switchFavori);
    });

// ADD FAVORI TO GROUP
$(function () {
    $('.transfert').click(function(event){
        event.preventDefault();
        var element = $(this);
        var group_id = $("#group_id").val();
        element.append("<i class='fa fa-spinner fa-spin fa-fw'></i>");
        $.ajax({
            url : '/user/groupe/switch_favori/',
            type : 'POST',
            data : {
                tune_slug : element.attr("data-id"),
                groupe_id : group_id
                },
                             complete: function () {
                     element.find("i:last").remove();
                 }, 
            success : function(response){
            if (response.status == "added"){
                element.hide();
                $("#added").prepend(`<tr><td>`+response.tune_name+`</td>
                            <td class="">`+response.tune_type+`</td>
                            <td class="">`+response.tune_key+`</td>
                            <td>added</td>
                            </tr>
                            `);
            }
            else if (response == "deleted"){
            }

            else {
                }
            }
            });
        });
    });

// STATUS FAVORIS
$(function () {
    $('.status').click(function(event){
        event.preventDefault();
        var element = $(this);
        element.append("<i class='fa fa-spinner fa-spin fa-fw'></i>");
        $.ajax({
            url : '/tune/switch_status/',
            type : 'POST',
            data : {
                tune_favori_slug : element.attr("data-id")
                },
                             complete: function () {
                     element.find("i:last").remove();
                 },
            success : function(response){
            if (response == "up"){
                element.children().addClass("fa-thumbs-up").removeClass("fa-thumbs-down");
                element.attr("data-original-title", gettext('Tune learnt'));
            }
            else if (response == "down"){
                element.children().addClass("fa-thumbs-down").removeClass("fa-thumbs-up");
                element.attr("data-original-title", gettext('Tune to learn'));
            }
            else {
                }
            }
            });
        });
    });

// SWITCH ROLE
$(function () {
    $('.choose_role').change(function(event){
        event.preventDefault();
        var element = $(this);
        var myself = "False";
        element.parent().append("<i class='fa fa-spinner fa-spin fa-fw'></i>");
        var ajaxCall = function(){
        $.ajax({
            url : '/user/groupe/switch_role/',
            type : 'POST',
            data : {
                user_role_id : element.attr("data-id"),
                user_role_value : element.val(),
                myself : myself
                },
                complete: function () {
                     element.parent().find("i:last").remove();
                 },
            success : function(response){
            if (response == "updated"){
                element.parent().append("<span class='updated'>updated</span>");
                $(".updated").fadeOut(1000, function(){this.remove()});
                if (myself == "True"){
                    location.href = "/user/groupe/liste/"
                }
            }
            else if (response == "last_one") {
                $.confirm({
                title: gettext('Warning'),
                content: gettext('You cannot remove the only Admin of the group'),
                columnClass: 'medium',
                type: 'red',
            });
                element.val("Admin");
                }
            else if (response =="warning"){
                $.confirm({
                title: gettext('Warning'),
                content: gettext('You are about to remove your Administrator rigths from this group. You will be redirected. Are you sure ?'),
                columnClass: 'medium',
                type: 'red',
                buttons: {
                    Cancel: function () {
                        element.val("Admin");
                    },
                    Ok: {
                        btnClass: 'btn-danger',
                        action: function(){
                            myself = "True";
                            ajaxCall();
                        }
                    }
                }
            });
                }  
            else {
                $.confirm({
                title: gettext('Warning'),
                content: gettext('An error occured'),
                columnClass: 'medium',
                type: 'red',
            });
                }
            }
            });
    };
    ajaxCall();
        });
    });

//Confirmation before delete favori
$(function () {
    //Pour chaque delete
    $(".unfavori").each(function () {
        $(this).click(function () {
            var submit = $(this);
            if (submit.attr("id")=="unfavori") {
                var label= submit.attr("data-id");
            } else {
            var label = submit.parents("tr").last().attr("data-id");
            }
            $.confirm({
                title: gettext('Remove "') + label + gettext('" from your favorites ?'),
                content: gettext('Are you sure to remove the Tune "') + label + gettext('" from your favorites ? Information linked with this favorite will be lost'),
                columnClass: 'medium',
                type: 'red',
                buttons: {
                    Cancel: function () {
                    },
                    Delete: {
                        btnClass: 'btn-danger',
                        action: function(){
                            $.ajax({
                                url : '/tune/tune_favori/delete/',
                                type : 'POST',
                                data : {
                                    tune_favori_slug : submit.attr("data-id")
                                },
                                success : function(response){
                                    if (submit.hasClass('remove_me')) {
                                    submit.parents("tr").last().remove();
                                } else {
                                        submit.children().addClass("fa-heart-o").removeClass("fa-heart");
                                        submit.attr("data-original-title", gettext('Tune removed from your favorites'));
                                        submit.removeClass("unfavori").addClass("favori");
                                        submit.unbind();
                                        submit.bind("click", switchFavori)
                                }
                                }
                            });
                        }
                    }
                }
            });
        });
    });
});

//Delete Sound
$(function () {
    //Pour chaque sound
    $(".remove_sound").each(function () {
        $(this).click(function () {
            var submit = $(this);
            var label = submit.attr("data-original-title");
            $.confirm({
                title: label,
                content: gettext('Information linked with this sound will be lost'),
                columnClass: 'medium',
                type: 'red',
                buttons: {
                    Cancel: function () {
                    },
                    Delete: {
                        btnClass: 'btn-danger',
                        action: function(){
                            $.ajax({
                                url : '/tune/sound/delete/',
                                type : 'POST',
                                data : {
                                    audio_slug : submit.attr("data-id")
                                },
                                success : function(response){
                                    if (response == "deleted"){
                                        submit.parents(".temp").last().remove();
                                    }
                                }
                            });
                        }
                    }
                }
            });
        });
    });
});

//CheckAll
$("#checkAll1_0").click(function () {
    $(".check1").prop('checked', true);
});
$("#checkAll1_1").click(function () {
    $(".check1").prop('checked', false);
});
$("#checkAll2_0").click(function () {
    $(".check2").prop('checked', true);
});
$("#checkAll2_1").click(function () {
    $(".check2").prop('checked', false);
});
$("#checkAll3").click(function () {
    $(".check3").prop('checked', $(this).prop('checked'));
});

//MENU : Change icon and name
$("[data-target='#sidebar']").click(function () {
    if ($(this).children().hasClass("fa-toggle-off")){
        $(this).html("<i class='fa fa-toggle-on' aria-hidden='true'></i> "+gettext('Hide Menu'));
        $.post( "/user/toggle_menu/", { boolean: true });
    }
    else {
        $(this).html("<i class='fa fa-toggle-off' aria-hidden='true'></i> "+gettext('Show Menu'));
        $.post( "/user/toggle_menu/", { boolean: false });
    }
    if ($("#sidebar").hasClass("in")) {
        $("#main").removeClass("col-xs-12 col-sm-9 col-md-10").addClass("col-xs-12");
    }
    else {
        $("#main").removeClass("col-xs-12").addClass("col-xs-12 col-sm-9 col-md-10");
    }
});

//MENU change arrows
$(function() {
  $('.list-group-item.chevron').on('click', function() {
    $('.fa-chevron-change', this)
      .toggleClass('fa-chevron-right')
      .toggleClass('fa-chevron-down');
  });
});


// We need these methods to add the CSRF token using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

//Force refresh le back
$(document).ready(function(e) {
    var $input = $('#refreshPrevious');
    $input.val() == 'yes' ? location.reload(true) : $input.val('yes');
});

//Ajout des popover
$(function () {
  $('[data-toggle="popover"]').popover()
})

//Ajout des tooltips
$(function () {
    $(".tooltipInfo").tooltip({trigger: 'hover'});
});