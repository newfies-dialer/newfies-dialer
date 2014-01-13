// code for datepicker in admin panel
$(function() {
    var dates = $('#id_from_date, #id_to_date').datepicker({
        defaultDate: "+1w",
        changeMonth: true,
        dateFormat: 'yy-mm-dd',
        onSelect: function(selectedDate) {
            var option = this.id == "id_from_date" ? "minDate" : "maxDate";
            var instance = $(this).data("datepicker");
            var date = $.datepicker.parseDate(instance.settings.dateFormat || $.datepicker._defaults.dateFormat, selectedDate, instance.settings);
            dates.not(this).datepicker("option", option, date);
        }
    });
});