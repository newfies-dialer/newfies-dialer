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
