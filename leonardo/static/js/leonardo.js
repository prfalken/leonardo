var Log = function(level) {
    this.level = level;
    this.levels = {"debug": 30, "warn": 20, "info": 10};
    this.active_debug = this.level >= this.levels.debug ? this.logger : this.null_logger;
    this.active_warn = this.level >= this.levels.warn ? this.logger : this.null_logger;
    this.active_info = this.level >= this.levels.info ? this.logger : this.null_logger;
}
Log.prototype.logger = function(lvl,msg) {
    console.log("[" + lvl + "] " + new Date() + ": " + msg);
}
Log.prototype.html_logger = function(lvl,msg) {
    document.write("<p><i>" + lvl + ": " + msg + "</i></p>");
}
Log.prototype.null_logger = function(lvl,msg) {
    return true;
}
Log.prototype.warn = function warn(msg) {
    this.active_warn("WARN", msg);
}
Log.prototype.debug = function debug(msg) {
    this.active_debug("DEBUG", msg);
}
Log.prototype.info = function info(msg) {
    this.active_info("INFO", msg);
}
var log = new Log(0);


function ms2s(ms) {
    return parseInt(ms/1000);
}

function s2ms(s) {
    return s*1000;
}


var leo = {
    version: "0.0.79",
    qso: {
        query: {
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
            keys = Object.keys(this.query);
            for (qk in keys ){
                if ( k == keys[qk] ) {
                    delete this.query[k];
                    return true
                }
            }
            log.debug("Can't delete a non existent key!");
            return false
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

            leo.qso.key(k,v);               // assign key/value pair to query string object.
            k = v = "";                     // re-initialise key/value variables.
        }
    },
    buildGraphiteDateString : function(date) {
        return ms2s(date.getTime());
    },
    formatSelectedDate : function(date) {
        return  zeroPad(date.getMonth() + 1) + "/"
                + zeroPad(date.getDate()) + "/"
                + date.getFullYear() + " "
                + zeroPad(date.getHours()) + ":"
                + zeroPad(date.getMinutes());
    },
    selectDateTime : function() {
        dt_from = new Date($('#dt_from').val());
        dt_to = new Date($('#dt_to').val());
        window.location = leo.buildGraphiteDateUrl(dt_from, dt_to);
        return true;
    },
    buildGraphiteDateUrl : function(dt_from, dt_to) {
        leo.qso.key("from", leo.buildGraphiteDateString(dt_from));
        leo.qso.key2cookie("from");
        leo.qso.key("until", leo.buildGraphiteDateString(dt_to));
        leo.qso.key2cookie("until");

        newurl = window.location.protocol + "//" + window.location.host
            + window.location.pathname ;

        // TODO: leo.qso.query needs to be encapsulated.
        querystring = "";
        if (Object.keys(leo.qso.query).length > 0) querystring = "?";

        for ( var k in leo.qso.query ) {
            querystring += k + "=" + leo.qso.query[k] + "&";
        }
        console.log(newurl + querystring);
        return newurl + querystring;
    },
    toggleSelectDate : function() {
        var tp = $('#dateTimePicker');

        tp.toggle(400);
        leo.toggleButton(tp);
    },
    toggleButton : function(o) {
        // o is expected to be a jquery object.
        var c = o.parent().attr("class");
        try {
            if ( c.search(/active/) == -1 ) {
                log.debug("Button to be activated "+ String(c) );
                o.parent().addClass("active");
            } else {
                log.debug("Button to be deactivated " + String(c));
                o.parent().removeClass("active");
            }
        }
        catch(e) {
            log.debug("<toggleButton> Something broke! " + e);
        }
    },
};


$(document).on('click', '.star', function(){
    $(this).attr('class', 'star-lit');
    $.cookie.raw = true;
    $.cookie("favorite", window.location.pathname, { expires: 365, path: '/' });
});

$(document).on('click', '.star-lit', function(){
    $(this).attr('class', 'star');
    $.removeCookie("favorite", { path: '/' });
});


$(function(){
    var needed_width = $('div.needed-width').width();
    $('div.graph img').each(function() {
        $(this).attr("src", $(this).attr('data-src').replace(/&width=[0-9]+/, "&width=" + needed_width));
    });
    console.log(needed_width);
});

