/* Javascript code for survey section page */

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