var leo = {
    qso: Object(),                           // query string object
    date_from: "-30min",
    date_to: "now",
    zeroPad: function(num) {
        return num < 10 ? String(num) : "0" + num;
    },
    getURLParameter : function(name) {
        return leo.qso[name];
    },
    transformQueryStringToObject : function(qs) {
        /*
         * Split query string into an array, then process the array for
         * key/value pairs to be stored as an object, which will later be
         * used to update/modify the pairs and reconstruct a new query string.
         */

        var qso = {};   // query string array
        var qsa = qs.split(/[&;=?]/);   // query string array
        var k="";                       // key name
        var v="";                       // value

        for ( var i = 0; i < qsa.length; i++ ) {

            if (k == "" && String(qsa[i]) == "") {
                continue;
            }

            if ( k == "" && v == "") {
                k = String(qsa[i]);
                continue;
            }

            if ( k != "" && v == "") {
                v = String(qsa[i]);
            }
            qso[k] = v;                 // assign key/value pair to query string object.
            k = v = "";                 // re-initialise key/value variables.
        }
        return qso;
    },
    removeURLParameter : function (qso, parameter) {
        if ( parameter in qso ) {
            delete qso[parameter];
        }
        return qso
    },
    buildGraphiteDateString : function(date) {
        return Math.round(date.getTime() / 1000);
    },
    setDestinationDate : function(srcDateBox, destDateBox, dateText)
    {
        if (destDateBox.val() == destDateBox.prop("defaultValue"))
            destDateBox.val(dateText);
        else {
            var startDate = $('#dt_from').datetimepicker('getDate');
            var endDate = $('#dt_to').datetimepicker('getDate');
            if (startDate > endDate)
                destDateBox.datetimepicker('setDate', srcDateBox.datetimepicker('getDate'));
        }
    },
    formatSelectedDate : function(date) {
        return  zeroPad(date.getMonth() + 1) + "/"
                + zeroPad(date.getDate()) + "/"
                + date.getFullYear() + " "
                + zeroPad(date.getHours()) + ":"
                + zeroPad(date.getMinutes());
    },
    getMethods : function(obj) {
        var result = [];
        for (var id in obj) {
            try {
                if (typeof(obj[id]) == "function") {
                    result.push(id + ": " + obj[id].toString());
                }
            } catch (err) {
                result.push(id + ": inaccessible");
            }
        }
        return result;
    },
    selectDt : function() {
        dt_from = new Date($('#dt_from').val());
        dt_to = new Date($('#dt_to').val());
        window.location = leo.buildGraphiteDateUrl(dt_from, dt_to);
        return true;
    },
    buildGraphiteDateUrl : function(dt_from, dt_to) {
        leo.qso["dt_from"] = leo.buildGraphiteDateString(dt_from);
        if ( "from" in leo.qso ) delete leo.qso.from;
        leo.qso["dt_to"]   = leo.buildGraphiteDateString(dt_to);
        if ( "to" in leo.qso ) delete leo.qso.to;

        newurl = window.location.protocol + "//" + window.location.host
            + window.location.pathname ;

        querystring = "";
        if (Object.keys(leo.qso).length > 0) querystring = "?";

        for ( var k in leo.qso ) {
            querystring += k + "=" + leo.qso[k] + "&";
        }
        console.log(newurl + querystring);
        return newurl + querystring;
    },
    toggleSelectDate : function() {
        $('#dateTimePicker').toggle(400);

    }
};

$(document).ready(function() {
    console.log("jquery V" + $.fn.jquery + "_13");

    leo.qso = leo.transformQueryStringToObject(window.location.search);

    $('#toggleDateTimePicker').parent().addClass('active');
    $('#dateTimePicker').hide();

    if ( "show_ds" in leo.qso ) {
        if ( leo.qso.show_ds != String(false) ) {
            leo.toggleSelectDate();
            leo.qso.show_ds = true;
        } else {
            leo.qso.show_ds = false;
        }
    }
});

$(function() {
    $('#toggleDateTimePicker').click(function() {
        leo.toggleSelectDate();
        leo.qso.show_ds = !leo.qso.show_ds;
        console.log(leo.qso.show_ds);
    });
});

$(function() {
    var startDateTextBox = $('#dt_from');
    var endDateTextBox = $('#dt_to');
    startDateTextBox.datetimepicker({
        dateFormat: 'yy-mm-dd',
        onClose: function(dateText, inst) {
            leo.setDestinationDate(startDateTextBox, endDateTextBox, dateText);
        }
    });
    endDateTextBox.datetimepicker({
        dateFormat: 'yy-mm-dd',
        onClose: function(dateText, inst) {
            leo.setDestinationDate(endDateTextBox, startDateTextBox, dateText);
        }
    });
});












