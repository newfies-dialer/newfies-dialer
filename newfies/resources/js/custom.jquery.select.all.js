function toggleChecked(status) {
        $(".checkbox").each( function() {
            $(this).attr("checked", status);
        })
    }

$(document).ready(function() {
    $('#ListForm').submit(function() {
        
        var $fields = $(this).find('input[name="select"]:checked');        
        if (!$fields.length) {
            alert('You must check at least one box!');
            return false; // The form will *not* submit
        }
        else
        {            
             var confirm_string;
             var contact_count;
             if(document.location.href.search("/voipapp/") != -1)
             {
                 confirm_string = 'you are going to delete '+$fields.length+' voipapp'
             }
             if(document.location.href.search("/contact/") != -1)
             {
                 confirm_string = 'you are going to delete '+$fields.length+' contact(s) from your phonebook'
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
                
                 confirm_string = 'you are going to delete '+$fields.length+' phonebook(s) with '+contact_count+' contact(s)'
             }             
             if(document.location.href.search("/campaign/") != -1)
             {
                 confirm_string = 'you are going to delete '+$fields.length+' campaign(s)'
             }
             var answer = confirm(confirm_string);             
             return answer // answer is a boolean
        }
    });
});