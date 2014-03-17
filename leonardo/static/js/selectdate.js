$(document).ready(function() {
    // process the query string.
    leo.transformQueryStringToObject(window.location.search);

    if($('#dt_from').val() != 'from')
        $('#toggleDateTimePicker').parent().addClass('active');
    else
        $('#dateTimePicker').hide();
});

$(function() {
    $('#toggleDateTimePicker').click(function() {
        $('#dateTimePicker').toggle(400);
    });
});

$(function() {
    var startDateTextBox = $('#dt_from');
    var endDateTextBox = $('#dt_to');
    startDateTextBox.datetimepicker({
        dateFormat: 'yy-mm-dd',
        onClose: function(dateText, inst) {
            setDestinationDate(startDateTextBox, endDateTextBox, dateText);
        }
    });
    endDateTextBox.datetimepicker({
        dateFormat: 'yy-mm-dd',
        onClose: function(dateText, inst) {
            setDestinationDate(endDateTextBox, startDateTextBox, dateText);
        }
    });
});


function setDestinationDate(srcDateBox, destDateBox, dateText) {
    if (destDateBox.val() == destDateBox.prop("defaultValue"))
        destDateBox.val(dateText);
    else {
        var startDate = $('#dt_from').datetimepicker('getDate');
        var endDate = $('#dt_to').datetimepicker('getDate');
        if (startDate > endDate)
            destDateBox.datetimepicker('setDate', srcDateBox.datetimepicker('getDate'));
    }
}