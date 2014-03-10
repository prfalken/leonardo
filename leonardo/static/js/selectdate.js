
function ms2s(ms) {
    return ms/1000;
}
function s2ms(s) {
    return s*1000;
}
var leo = {
    version: 61,
    qso: {
        query: {
            show_ds: undefined,
            from: undefined,
            until: undefined
        },
        has_key: function(k){
            o_keys = Object.keys(this.query);
            for ( var ko in o_keys ) {
                if ( k == o_keys[ko] ) return true;
            }
            return false;
        },
        _key: function(k) {
            if (this.has_key(k)) return this.query[k];
            return undefined;
        },
        key: function(k,v) {
            if (v == undefined) return this._key(k);
            this.query[k]=v;
        },
        del_key : function (k) {
            if ( k in Object.keys(this.query) ) delete this.query[k];
        },
        key2cookie: function(k) {
            $.cookie(k, this.key(k),{path:"/"});
        }
    },
    zeroPad: function(num) {
        return num < 10 ? String(num) : "0" + num;
    },
    transformQueryStringToObject : function(qs) {
        /*
         * Split query string into an array, then process the array for
         * key/value pairs to be stored as an object, which will later be
         * used to update/modify the pairs and reconstruct a new query string.
         */
        var qsa = qs.split(/[&;=?]/);   // query string array
        var k="";                       // key name
        var v="";                       // value

        for ( var i = 0; i < qsa.length; i++ ) {

            if ( k == "" && String(qsa[i]) == "" ) { continue; }

            if ( k == "" && v == "" ) {
                k = String(qsa[i]);
                continue;
            }

            if ( k != "" && v == "" ) { v = String(qsa[i]); }

            leo.qso[k] = v;                 // assign key/value pair to query string object.
            k = v = "";                     // re-initialise key/value variables.
        }
    },
    buildGraphiteDateString : function(date) {
        return ms2s(Math.round(date.getTime()));
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

                $.cookie("from", new Date(startDate.val()).getTime()/1000, {path: "/", domain: window.location.host});
                $.cookie("until", new Date(endDate.val()).getTime()/1000, {path: "/", domain: window.location.host});
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
        leo.qso["from"] = leo.buildGraphiteDateString(dt_from);
        leo.qso["until"]   = leo.buildGraphiteDateString(dt_to);
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
    console.log("jquery V" + $.fn.jquery + "_" + leo.version);

    leo.transformQueryStringToObject(window.location.search);

    $('#toggleDateTimePicker').parent().addClass('active');
    $('#dateTimePicker').hide();
});


$(function() {
    /* when the page loads, leonardo checks for query string and cookie
    parameters.
    * Query strings take priority over cookies.
    * Cookies are used in the absence of Query strings.
    * cookies or query strings are only cast to Date objects if they're
    * digits.  Otherwised they're passed through.
*/
    /*
     * 1. Get the query string values. show_ds, from and until.
     * 2. If any query string keys are missing, check for them in the cookies.
     * 3. Determine if the from and until values are epoch timestamps.
     *   3.1 Set date picker for each key that has an epoch timestamp.
     */
    if(leo.qso.has_key("show_ds")){
        leo.qso.key2cookie("show_ds");
    }
    var show_ds = $.cookie("show_ds");
    if ( show_ds == undefined ) {
        show_ds = false;
    } else if ( show_ds == String(true) ) {
        show_ds = true;
    } else {
        show_ds = false;
    }
    leo.qso.key("show_ds",show_ds);
    leo.qso.key2cookie("show_ds");
    if (leo.qso.key("show_ds")) leo.toggleSelectDate();

    if(leo.qso.has_key("from")){
        leo.qso.key2cookie("from");
    }
    var dt_from = $.cookie("from");
    if ( dt_from == undefined ) {
        dt_from = ms2s(new Date().getTime()) - 30*60;
        $("#dt_from").datepicker("setDate", new Date(s2ms(dt_from)));
        $("#dt_from").datepicker("refresh");
    } else if ( dt_from.match(/^\d+$/) ) {
        $("#dt_from").datepicker("setDate", new Date(s2ms(parseInt(dt_from))));
        $("#dt_from").datepicker("refresh");
    }
    leo.qso.key("from",dt_from);
    leo.qso.key2cookie("from");

    if(leo.qso.has_key("until")){
        leo.qso.key2cookie("until");
        leo.qso.del_key("to");
        $.cookie("to","",{path: "/", expires: -1})
    }
    var dt_to = $.cookie("until");
    if ( dt_to == undefined ) {
        dt_to = ms2s(new Date().getTime())-1;
        $("#dt_to").datepicker("setDate", new Date(s2ms(dt_to)));
        $("#dt_to").datepicker("refresh");
    } else if ( dt_to.match(/^\d+$/) ) {
        $("#dt_to").datepicker("setDate", new Date(s2ms(parseInt(dt_to))));
        $("#dt_to").datepicker("refresh");
    }
    leo.qso.key("until",dt_to);
    leo.qso.key2cookie("until");

});

$(function() {
    $('#toggleDateTimePicker').click(function() {
        leo.toggleSelectDate();
        leo.qso.key("show_ds", !leo.qso.key("show_ds"));
        leo.qso.key2cookie("show_ds");
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




