/* Javascript code for survey section page */

function toggleChecked(status) {
    $(".checkbox").each(function() {
        $(this).prop("checked", status);
    });
}

function bootbox_call(confirm_string, href)
{
    bootbox.confirm(confirm_string, function(result){
        if (result) {
            window.location = href;
        }
    });
    return true;
}

function ajax_call(url, ids)
{
    contact_count = 0;
    $.ajax({
        url: url,
        type: "GET",
        async: false,
        cache: false,
        timeout: 30000,
        data: "ids=" + ids,
        success: function(data) {
            contact_count = data;
        },
        // error: function() {
        //     alert("Request failed");
        // }
    });
    return contact_count;
}

var campaign_stop_flag;
$(function () {
    $('#ListForm').submit(function(e) {

        var currentForm = this;
        e.preventDefault();

        var $fields = $(this).find('input[name="select"]:checked');

        if (!$fields.length) {
            msg = gettext("You must check at least one box!");
            bootbox.alert(msg);
            return false; // The form will *not* submit
        } else {
            var confirm_string;
            var contact_count;

            if(document.location.href.search("/contact/") != -1) {
                confirm_string = $fields.length +  gettext(" contact(s) are going to be deleted?") ;
            }
            if(document.location.href.search("/survey/") != -1) {
                confirm_string = $fields.length + gettext(" survey(s) are going to be deleted?");
            }
            if(document.location.href.search("/audio/") != -1) {
                confirm_string = $fields.length + gettext(" audio(s) are going to be deleted?");
            }
            if(document.location.href.search("/phonebook/") != -1) {
                var allVals = [];
                $fields.each(function() {
                   allVals.push($(this).val());
                });
                contact_count = ajax_call("/phonebook/contact_count/", allVals);
                confirm_string = $fields.length + gettext(" phonebook(s) are going to be deleted with ") + contact_count + gettext(" contact(s)?");
            }
            if(document.location.href.search("/campaign/") != -1) {
                if (campaign_stop_flag) {
                    $("#ListForm").attr("action", "del/0/?stop_campaign=True");
                    confirm_string = $fields.length + gettext(" campaign(s) are going to be stopped?");
                    campaign_stop_flag = false;
                } else {
                    confirm_string = $fields.length + gettext(" campaign(s) are going to be deleted?");
                }
            }
            if(document.location.href.search("/survey/") != -1) {
                confirm_string = $fields.length + gettext(" survey(s) are going to be deleted?");
            }
            if(document.location.href.search("/dnc_list/") != -1) {

                var allVals = [];
                $fields.each(function() {
                   allVals.push($(this).val());
                });
                contact_count = ajax_call("/module/dnc_list/contact_count/", allVals);
                confirm_string = $fields.length + gettext(" DNC(s) are going to be deleted with ") + contact_count + gettext(" contact(s)?");
            }
            if(document.location.href.search("/dnc_contact/") != -1) {
                confirm_string = $fields.length +  gettext(" DNC contact(s) are going to be deleted?") ;
            }
            if(document.location.href.search("/agent/") != -1) {
                confirm_string = $fields.length +  gettext(" agent(s) are going to be deleted?") ;
            }
            if(document.location.href.search("/queue/") != -1) {
                confirm_string = $fields.length +  gettext(" queue(s) are going to be deleted?");
            }
            if(document.location.href.search("/tier/") != -1) {
                confirm_string = $fields.length +  gettext(" tier(s) are going to be deleted?");
            }
            if(document.location.href.search("/calendar_setting/") != -1) {
                confirm_string = $fields.length +  gettext(" calendar setting(s) are going to be deleted?");
            }
            if(document.location.href.search("/calendar_user/") != -1) {
                confirm_string = $fields.length +  gettext(" calendar user(s) are going to be deleted?");
            }
            if(document.location.href.search("/calendar/") != -1) {
                confirm_string = $fields.length +  gettext(" calendar(s) are going to be deleted?");
            }
            if(document.location.href.search("/event/") != -1) {
                confirm_string = $fields.length +  gettext(" event(s) are going to be deleted?");
            }
            if(document.location.href.search("/alarm/") != -1) {
                confirm_string = $fields.length +  gettext(" alarm(s) are going to be deleted?");
            }

            if(document.location.href.search("/sms_campaign/") != -1) {
                if(sms_campaign_stop_flag){

                    $("#ListForm").attr("action", "del/0/?stop_sms_campaign=True");
                    confirm_string = $fields.length + gettext(" sms campaign(s) are going to be stopped?");
                    sms_campaign_stop_flag = false;
                }
                else{
                    confirm_string = $fields.length + gettext(" sms campaign(s) are going to be deleted?");
                }
            }

            bootbox.confirm(confirm_string, function(result) {
                if (result) {
                    currentForm.submit();
                }
            });
            return false;
        }
    });

    $('a[id="id_delete_confirm"]').click(function(e) {
        e.preventDefault();
        var href = this.href;
        confirm_string = gettext("confirm deletion?");
        bootbox_call(confirm_string, href);
        return false;
    });
});

function get_alert_msg_for_phonebook(id)
{
    contact_count = ajax_call("/phonebook/contact_count/", id);
    var href = $('#id_phonebook_delete_confirm-' + id).attr('href');
    confirm_string = gettext("Please press OK to delete this phonebook with") + ' ' + contact_count + ' ' + gettext("contact(s)");
    bootbox_call(confirm_string, href);
    return false;
}

function get_alert_msg_for_dnc(id)
{
    contact_count = ajax_call("/module/dnc_list/contact_count/", id);
    var href = $('#id_dnc_delete_confirm-' + id).attr('href');
    alert(href);
    confirm_string = gettext("Please press OK to delete this DNC with") + ' ' + contact_count + ' ' + gettext("contact(s)");
    bootbox_call(confirm_string, href);
    return false;
}

function add_button() {
    window.location = 'add/';
}

function delete_button() {
    $('#ListForm').submit();
}

function campaign_stop_button() {
    campaign_stop_flag = true;
    $('#ListForm').submit();
}

var sms_campaign_stop_flag;
function sms_campaign_stop_button(){
    sms_campaign_stop_flag = true;
    $('#ListForm').submit();
}

//////////////////////
// Datepicker code ///
//////////////////////

$("#id_from_date_picker").on("change.dp",function (e) {
   $('#id_to_date_picker').data("DateTimePicker").setStartDate(e.date);
});
$("#id_to_date_picker").on("change.dp",function (e) {
   $('#id_from_date_picker').data("DateTimePicker").setEndDate(e.date);
});

$("#id_startingdate_picker").on("change.dp",function (e) {
   $('#id_expirationdate_picker').data("DateTimePicker").setStartDate(e.date);
});
$("#id_expirationdate_picker").on("change.dp",function (e) {
   $('#id_startingdate_picker').data("DateTimePicker").setEndDate(e.date);
});

if(document.location.href.search("/calendar/") != -1 || document.location.href.search("/alarm/") != -1 ) {

    $("#id_start_picker").on("change.dp",function (e) {
       $('#id_end_picker').data("DateTimePicker").setStartDate(e.date);
    });
    $("#id_end_picker").on("change.dp",function (e) {
       $('#id_start_picker').data("DateTimePicker").setEndDate(e.date);
    });
}

/// toggle code///
/// convert checkbox into switch button ///
$(function() {
  // initialize all the inputs
  $('.make-switch>input[type="checkbox"],[type="radio"]').bootstrapSwitch();
});


$(function () {
    $('#helpover').popover();
    $(".fg-button").hover(
        function(){
            $(this).addClass("ui-state-hover");
        },
        function(){
            $(this).removeClass("ui-state-hover");
        }
    );
    $('#buttonlogin').click(function(){
      $("#requestlogin").animate({ height: 'show', opacity: 'show' }, 'slow');
    });
    $("#language-container").change(function() {
        this.form.submit();
    });
});

// toggle event for hide/open search button
$(function() {

    $("#form_collapse").on('hidden.bs.collapse', function() {
        $('#toggle_btn_i_span').text(gettext('open search'));
        $('#toggle_btn_i').attr('class', 'glyphicon glyphicon-zoom-in');
    });

    $("#form_collapse").on('shown.bs.collapse', function() {
        $('#toggle_btn_i_span').text(gettext('hide search'));
        $('#toggle_btn_i').attr('class', 'glyphicon glyphicon-zoom-out');
    });
});