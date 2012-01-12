function toggleChecked(status) {
        $(".checkbox").each( function() {
            $(this).attr("checked", status);
        })
    }

$(document).ready(function() {
    $('#ListForm').submit(function() {
        
        var $fields = $(this).find('input[name="select"]:checked');

        if (!$fields.length) {
            alert(gettext('You must check at least one box!'));
            return false; // The form will *not* submit
        }
        else
        {            
             var confirm_string;
             var contact_count;
             if(document.location.href.search("/voiceapp/") != -1)
             {
                 confirm_string = $fields.length + ' ' + gettext('voice app(s) are going to be deleted') + '?'
             }
             if(document.location.href.search("/contact/") != -1)
             {
                 confirm_string = $fields.length + ' ' + gettext('phonebook(s) are going to be deleted') + '?'
             }
             if(document.location.href.search("/survey/") != -1)
             {
                 confirm_string = $fields.length + ' ' + gettext('survey(s) are going to be deleted') + '?'
             }
             if(document.location.href.search("/audio/") != -1)
             {
                 confirm_string = $fields.length + ' ' + gettext('audio(s)' + ' are going to be deleted') + '?'
             }
             if(document.location.href.search("/phonebook/") != -1)
             {
                var allVals = [];                
                $fields.each(function() {
                   allVals.push($(this).val());                   
                });                                 
                $.ajax({
                    url: "http://127.0.0.1:8000/dialer_campaign/phonebook/contact_count/",
                    type: "GET",
                    async: false,
                    cache: false,
                    timeout: 30000,
                    data: "pb_ids=" + allVals,
                    success: function(data) {                                                
                        contact_count = data;                                               
                    },
                    error: function() {
                        alert("Request failed");
                    }
                });
                
                 confirm_string = $fields.length + ' ' + gettext('phonebook(s) are going to be deleted with') + ' ' + contact_count+ ' ' + gettext('contact(s)') + '?'
             }             
             if(document.location.href.search("/campaign/") != -1)
             {
                 confirm_string = $fields.length + ' ' + gettext('campaign(s) are going to be deleted') + '?'
             }

             if(document.location.href.search("/user_detail_change/") != -1)
             {
                 confirm_string = $fields.length + ' ' + gettext('notification(s) are going to be deleted') + '?'
                 
                 if(document.getElementById('id_mark_read').value == 'true')
                 {
                   confirm_string = $fields.length + ' ' + gettext('notification(s) are going to be marked as read') + '?'
                 }
             }

             var answer = confirm(confirm_string);             
             return answer // answer is a boolean
        }
    });
});