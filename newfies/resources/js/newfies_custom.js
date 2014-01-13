/* Javascript code for survey section page */

function call_function(branch_id) {
    var goto_id = $('#id_branching_goto_' + String(branch_id) ).val();
    Dajaxice.survey.default_branching_goto(Dajax.process, {'id': branch_id, 'goto_id': goto_id});
}

// To sort question
function section_sort(id, sort_order) {
    Dajaxice.survey.section_sort(Dajax.process, {'id': id, 'sort_order': sort_order});
}

$(document).ready(function(){
    $(".column").sortable({
        update: function(event, ui) {
            // survey question sorting logic
            var result = $('.column').sortable('toArray');
            j = 1; // sort order
            for(i = 0; i < (result.length); i++) {
                section_sort(result[i].split('row')[1], j);
                j++;
            }
        },
        handle: '.fa-arrows'
    });

    //Add move button
    $(".portlet")
        .addClass("ui-widget ui-widget-content ui-helper-clearfix ui-corner-all")
        .find(".portlet-header")
        .addClass("ui-widget-header ui-corner-all")
        .append('<a class="btn btn-xs right-side-icon" role="button" href="#" title="{% trans "move"|title %}"><i class="fa fa-arrows"></i></a>')
        .end()
        .find(".portlet-content");

    //Add toggle button
    $(".portlet")
        .addClass("ui-widget ui-widget-content ui-helper-clearfix ui-corner-all")
        .find(".portlet-header")
        .addClass("ui-widget-header ui-corner-all")
        .append('<a class="btn btn-xs right-side-icon" role="button"  href="#" title="{% trans "collapse"|title %}"><i class="fa fa-arrow-circle-up"></i></a>')
        .end()
        .find(".portlet-content");

    //Add Section delete button
    $(".portlet")
        .addClass("ui-widget ui-widget-content ui-helper-clearfix ui-corner-all")
        .find(".portlet-header")
        .addClass("ui-widget-header ui-corner-all")
        .append('<a class="section-delete btn btn-xs right-side-icon" role="button"  href="#" title="{% trans "delete section"|title %}"><i class="fa fa-trash-o"></i></a>')
        .end()
        .find(".portlet-content");

    //Add Branch button
    $(".portlet")
        .addClass("ui-widget ui-widget-content ui-helper-clearfix ui-corner-all")
        .find(".portlet-header")
        .addClass("ui-widget-header ui-corner-all")
        .append('<a class="section-branch btn btn-xs right-side-icon" role="button"  href="#" title="{% trans "branch"|title %}"><i class="fa fa-random"></i></a>')
        .end()
        .find(".portlet-content");

    //Add Section edit button
    $(".portlet")
        .addClass("ui-widget ui-widget-content ui-helper-clearfix ui-corner-all")
        .find(".portlet-header")
        .addClass("ui-widget-header ui-corner-all")
        .append('<a class="section-edit btn btn-xs right-side-icon" role="button"  href="#" title="{% trans "edit section"|title %}"><i class="fa fa-pencil fa-fw"></i></a>')
        .end()
        .find(".portlet-content");

    //Handle toggle click to show and hide section details
    $(".portlet-header .btn-xs .fa-arrow-circle-up").click(function() {
        $(this).toggleClass("fa-arrow-circle-up").toggleClass("fa-arrow-circle-down");
        $(this).parents(".portlet:first").find(".portlet-content").toggle();
    });
});