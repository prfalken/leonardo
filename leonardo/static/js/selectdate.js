$(function()
{
    // process the query string.
    leo.transformQueryStringToObject(window.location.search);

    if($('#dt_from').val() != '')
    {
        $('#toggleDateTimePicker').removeClass('active').hide();
        $('#dateTimePicker').fadeIn('fast');
    }

    $("div.graph-control-panel").hide();
    $("div.graph").hover(
        function() {
            $(this).children(".graph-control-panel").toggle(0);
        },
        function()
        {
            $(this).children(".graph-control-panel").toggle(50);
        }
    );

    $('#toggleDateTimePicker').click(function() {
        $(this).animate({width: '0px', opacity: 0});
        $('.nav li').removeClass('active');
        $('#dateTimePicker').fadeIn('fast');
    });

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
