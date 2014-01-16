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